import { create } from "zustand";
import { conversationsApi } from "@/lib/api/conversations";
import type { Conversation } from "@/types";

interface ConversationState {
  conversations: Conversation[];
  activeId: string | null;
  loading: boolean;
  searchQuery: string;

  fetchAll: () => Promise<void>;
  setActive: (id: string | null) => void;
  setSearchQuery: (q: string) => void;
  remove: (id: string) => Promise<void>;
  /** Optimistically add/update a conversation, e.g. right after the first
   *  message of a brand-new chat comes back with a conversation_id. */
  upsertLocal: (conversation: Conversation) => void;
}

export const useConversationStore = create<ConversationState>((set, get) => ({
  conversations: [],
  activeId: null,
  loading: false,
  searchQuery: "",

  fetchAll: async () => {
    set({ loading: true });
    try {
      const conversations = await conversationsApi.list();
      set({ conversations, loading: false });
    } catch {
      // Backend conversations endpoint may not exist yet — fail soft,
      // the sidebar just shows whatever's been upserted locally so far.
      set({ loading: false });
    }
  },

  setActive: (id) => set({ activeId: id }),
  setSearchQuery: (searchQuery) => set({ searchQuery }),

  remove: async (id) => {
    const previous = get().conversations;
    set({ conversations: previous.filter((c) => c.id !== id) });
    try {
      await conversationsApi.remove(id);
    } catch {
      set({ conversations: previous }); // roll back on failure
    }
  },

  upsertLocal: (conversation) =>
    set((state) => {
      const exists = state.conversations.some((c) => c.id === conversation.id);
      return {
        conversations: exists
          ? state.conversations.map((c) =>
              c.id === conversation.id ? conversation : c
            )
          : [conversation, ...state.conversations]
      };
    })
}));
