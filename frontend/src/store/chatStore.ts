import { create } from "zustand";
import { chatApi } from "@/lib/api/chat";
import { conversationsApi } from "@/lib/api/conversations";
import { useConversationStore } from "@/store/conversationStore";
import type { ChatMessage } from "@/types";

interface ChatState {
  messagesByConversation: Record<string, ChatMessage[]>;
  isAssistantTyping: boolean;
  error: string | null;

  messagesFor: (conversationId: string | null) => ChatMessage[];

  appendMessage: (
    conversationId: string,
    role: "user" | "assistant",
    content: string,
    audioUrl?: string
  ) => void;

  setMessages: (conversationId: string, messages: ChatMessage[]) => void;

  loadConversation: (conversationId: string) => Promise<void>;

  sendMessage: (
    conversationId: string | null,
    text: string
  ) => Promise<{ conversationId: string }>;

  reset: (conversationId: string) => void;
}

function tempId() {
  return `tmp_${Math.random().toString(36).slice(2)}`;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messagesByConversation: {},
  isAssistantTyping: false,
  error: null,

  messagesFor: (conversationId) =>
    conversationId
      ? get().messagesByConversation[conversationId] ?? []
      : [],

  appendMessage: (
    conversationId,
    role,
    content,
    audioUrl
  ) =>
    set((state) => ({
      messagesByConversation: {
        ...state.messagesByConversation,
        [conversationId]: [
          ...(state.messagesByConversation[conversationId] ?? []),
          {
            id: tempId(),
            conversationId,
            role,
            content,
            createdAt: new Date().toISOString(),
            audioUrl: audioUrl ?? null
          }
        ]
      }
    })),

  setMessages: (conversationId, messages) =>
    set((state) => ({
      messagesByConversation: {
        ...state.messagesByConversation,
        [conversationId]: messages
      }
    })),

  /**
   * Fetches full message history for a conversation from the backend
   * (GET /conversations/:id) and hydrates the store — but only if we
   * don't already have messages for it locally (avoids clobbering
   * messages that were just optimistically appended in this session).
   */
  loadConversation: async (conversationId) => {
    const existing = get().messagesByConversation[conversationId];
    if (existing && existing.length > 0) return;

    try {
      const { messages } = await conversationsApi.get(conversationId);

      // Re-check in case messages arrived while the request was in flight.
      // Grabbed into a local var (rather than indexing twice) so TS can
      // narrow it from ChatMessage[] | undefined to ChatMessage[] below.
      const current = get().messagesByConversation[conversationId];
      const stillEmpty = !current || current.length === 0;

      if (stillEmpty) {
        get().setMessages(conversationId, messages);
      }
    } catch {
      // Conversation might be brand-new / not yet on the backend — fail soft.
    }
  },

  sendMessage: async (conversationId, text) => {
    const draftKey = conversationId ?? "__draft__";

    const userMessage: ChatMessage = {
      id: tempId(),
      conversationId: draftKey,
      role: "user",
      content: text,
      createdAt: new Date().toISOString()
    };

    set((state) => ({
      messagesByConversation: {
        ...state.messagesByConversation,
        [draftKey]: [
          ...(state.messagesByConversation[draftKey] ?? []),
          userMessage
        ]
      },
      isAssistantTyping: true,
      error: null
    }));

    try {
      const res = await chatApi.send(
        text,
        conversationId
      );

      const assistantMessage: ChatMessage = {
        id: tempId(),
        conversationId: res.conversation_id,
        role: "assistant",
        content: res.response,
        createdAt: new Date().toISOString()
      };

      set((state) => {
        const priorDraft =
          state.messagesByConversation[draftKey] ?? [];

        const merged =
          draftKey === res.conversation_id
            ? priorDraft
            : priorDraft.map((m) => ({
                ...m,
                conversationId:
                  res.conversation_id
              }));

        const existing =
          draftKey === res.conversation_id
            ? []
            : state.messagesByConversation[
                res.conversation_id
              ] ?? [];

        const rest = {
          ...state.messagesByConversation
        };

        delete rest[draftKey];

        return {
          messagesByConversation: {
            ...rest,
            [res.conversation_id]: [
              ...existing,
              ...merged,
              assistantMessage
            ]
          },
          isAssistantTyping: false
        };
      });

      useConversationStore
        .getState()
        .upsertLocal({
          id: res.conversation_id,
          title: text.slice(0, 50),
          updatedAt: new Date().toISOString()
        });

      return {
        conversationId:
          res.conversation_id
      };
    } catch (err) {
      set({
        isAssistantTyping: false,
        error:
          err instanceof Error
            ? err.message
            : "Failed to reach NuroFlow."
      });

      throw err;
    }
  },

  reset: (conversationId) =>
    set((state) => {
      const rest = {
        ...state.messagesByConversation
      };

      delete rest[conversationId];

      return {
        messagesByConversation: rest
      };
    })
}));