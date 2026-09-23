import { create } from "zustand";
import { notionApi } from "@/lib/api/notion";

interface NotionState {
  connected: boolean;
  /** null until the first status check resolves, so the UI can show
   *  a neutral "checking…" state instead of flashing "not connected". */
  checked: boolean;
  loading: boolean;
  error: string | null;

  fetchStatus: () => Promise<void>;
  connect: () => void;
  disconnect: () => Promise<void>;
}

export const useNotionStore = create<NotionState>((set) => ({
  connected: false,
  checked: false,
  loading: false,
  error: null,

  fetchStatus: async () => {
    set({ loading: true, error: null });
    try {
      const status = await notionApi.getStatus();
      set({ connected: status.connected, checked: true, loading: false });
    } catch (err) {
      set({
        loading: false,
        checked: true,
        connected: false,
        error: err instanceof Error ? err.message : "Could not check Notion connection."
      });
    }
  },

  connect: () => {
    window.location.href = notionApi.connectUrl();
  },

  disconnect: async () => {
    set({ loading: true, error: null });
    try {
      const status = await notionApi.disconnect();
      set({ connected: status.connected, loading: false });
    } catch (err) {
      set({
        loading: false,
        error: err instanceof Error ? err.message : "Could not disconnect Notion."
      });
    }
  }
}));