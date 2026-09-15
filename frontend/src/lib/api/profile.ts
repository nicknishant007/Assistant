import { apiClient } from "./client";
import type { UserProfile, ProfileUpdateInput } from "@/types";

export const profileApi = {
  async get(): Promise<UserProfile> {
    const { data } = await apiClient.get("/api/profile");
    return data;
  },

  async update(input: ProfileUpdateInput): Promise<UserProfile> {
    const { data } = await apiClient.put("/api/profile", input);
    return data;
  }
};