import { create } from "zustand";
import { preferencesApi } from "@/lib/api/preferences";
import type { UserPreferences, PreferencesUpdateInput } from "@/types";

interface PreferencesState {
  preferences: UserPreferences | null;
  loading: boolean;
  error: string | null;

  fetchPreferences: () => Promise<void>;
  updatePreferences: (input: PreferencesUpdateInput) => Promise<void>;
}

export const usePreferencesStore = create<PreferencesState>((set) => ({
  preferences: null,
  loading: false,
  error: null,

  fetchPreferences: async () => {
    set({ loading: true, error: null });
    try {
      const preferences = await preferencesApi.get();
      set({ preferences, loading: false });
    } catch (err) {
      set({
        loading: false,
        error: err instanceof Error ? err.message : "Could not load preferences."
      });
    }
  },

  updatePreferences: async (input) => {
    const updated = await preferencesApi.update(input);
    set({ preferences: updated });
  }
}));