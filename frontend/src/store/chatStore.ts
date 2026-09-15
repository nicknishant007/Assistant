import { create } from "zustand";
import { chatApi } from "@/lib/api/chat";
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
    audioUrl?:string
  ) => void;

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
            audioUrl:audioUrl ?? null
          }
        ]
      }
    })),

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