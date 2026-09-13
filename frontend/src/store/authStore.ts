import { create } from "zustand";
import { authApi } from "@/lib/api/auth";
import type { User } from "@/types";

interface AuthState {
  user: User | null;
  status: "idle" | "loading" | "authenticated" | "unauthenticated";
  error: string | null;

  /** Call once on app load (root layout) to hydrate from the session cookie. */
  hydrate: () => Promise<void>;
  logout: () => Promise<void>;
  loginWithGoogle: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  status: "idle",
  error: null,

  hydrate: async () => {
    set({ status: "loading" });
    try {
      const user = await authApi.me();
      set({ user, status: "authenticated", error: null });
    } catch {
      set({ user: null, status: "unauthenticated" });
    }
  },

  logout: async () => {
    await authApi.logout();
    set({ user: null, status: "unauthenticated" });
  },

  loginWithGoogle: () => {
    window.location.href = authApi.googleLoginUrl();
  }
}));
