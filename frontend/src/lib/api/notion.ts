import { apiClient } from "./client";

/**
 * Maps to Backend/api/routes/notion.py. Login is a redirect (same
 * pattern as Google in lib/api/auth.ts) rather than a POST — the
 * backend needs a full browser navigation to hand off to Notion's
 * OAuth page and back.
 */

export interface NotionConnectionStatus {
  connected: boolean;
  provider: "notion";
}

export const notionApi = {
  async getStatus(): Promise<NotionConnectionStatus> {
    const { data } = await apiClient.get("/api/notion/connection");
    return data;
  },

  /** Full backend URL that kicks off the Notion OAuth redirect. */
  connectUrl(): string {
    return `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/notion/login`;
  },

  async disconnect(): Promise<NotionConnectionStatus> {
    const { data } = await apiClient.post("/api/notion/disconnect");
    return data;
  }
};