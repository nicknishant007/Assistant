import { apiClient } from "./client";
import type { Conversation, ChatMessage } from "@/types";

/**
 * NOTE — backend gap: Backend/main.py does not currently register a
 * conversations router (only auth, chat, scheduler, voice). The data
 * exists (Backend/services/conversation_service.py, ConversationMessage
 * model) but isn't exposed over HTTP yet. This module assumes the
 * straightforward REST surface described in the brief:
 *
 *   GET    /conversations
 *   GET    /conversations/:id
 *   DELETE /conversations/:id
 *
 * conversationStore degrades gracefully (falls back to local-only
 * history) if these 404 — see store/conversationStore.ts — so the rest
 * of the app isn't blocked on that backend work landing.
 */
export const conversationsApi = {
  async list(): Promise<Conversation[]> {
    const { data } = await apiClient.get("/conversations");
    return data;
  },

  async get(id: string): Promise<{ conversation: Conversation; messages: ChatMessage[] }> {
    const { data } = await apiClient.get(`/conversations/${id}`);
    return data;
  },

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/conversations/${id}`);
  }
};
