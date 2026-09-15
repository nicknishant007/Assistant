import { create } from "zustand";
import { profileApi } from "@/lib/api/profile";
import type { UserProfile, ProfileUpdateInput } from "@/types";

interface ProfileState {
  profile: UserProfile | null;
  loading: boolean;
  error: string | null;

  fetchProfile: () => Promise<void>;
  updateProfile: (input: ProfileUpdateInput) => Promise<void>;
}

export const useProfileStore = create<ProfileState>((set) => ({
  profile: null,
  loading: false,
  error: null,

  fetchProfile: async () => {
    set({ loading: true, error: null });
    try {
      const profile = await profileApi.get();
      set({ profile, loading: false });
    } catch (err) {
      set({
        loading: false,
        error: err instanceof Error ? err.message : "Could not load profile."
      });
    }
  },

  updateProfile: async (input) => {
    const updated = await profileApi.update(input);
    set({ profile: updated });
  }
}));