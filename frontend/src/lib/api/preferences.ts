import { apiClient } from "./client";
import type { UserPreferences, PreferencesUpdateInput } from "@/types";

export const preferencesApi = {
  async get(): Promise<UserPreferences> {
    const { data } = await apiClient.get("/api/preferences");
    return data;
  },

  async update(input: PreferencesUpdateInput): Promise<UserPreferences> {
    const { data } = await apiClient.put("/api/preferences", input);
    return data;
  }
};