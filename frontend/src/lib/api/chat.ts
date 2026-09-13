import { apiClient } from "./client";
import type { ChatResponse } from "@/types";

export const chatApi = {
  async send(message: string, conversationId: string | null): Promise<ChatResponse> {
    const { data } = await apiClient.post<ChatResponse>("/chat", {
      conversation_id: conversationId,
      message
    });
    return data;
  }
};
