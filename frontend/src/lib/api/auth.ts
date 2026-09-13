import { apiClient } from "./client";
import type { User } from "@/types";

/**
 * Auth is Google-OAuth-only on the backend today (Backend/api/routes/auth.py):
 * there is no email/password endpoint, login is a redirect to Google and
 * the backend sets the session cookie on callback. We expose that as a
 * simple "go to this URL" helper rather than pretending a form exists.
 */
export const authApi = {
  /** Full backend URL to kick off the Google OAuth redirect. */
  googleLoginUrl(): string {
    return `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/auth/login/google`;
  },

  async me(): Promise<User> {
    const { data } = await apiClient.get("/api/auth/me");
    return { id: data.id, email: data.email, name: data.name };
  },

  async logout(): Promise<void> {
    await apiClient.post("/api/auth/logout");
  }
};
