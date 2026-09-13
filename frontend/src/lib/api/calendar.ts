import { apiClient } from "./client";
import type { CalendarEvent, CreateEventInput, UpdateEventInput } from "@/types";

/**
 * Maps to Backend/api/routes/auth.py's /api/auth/events* endpoints
 * (calendar lives under the auth router today because event creation
 * needs the Google integration tied to the logged-in user).
 */
export const calendarApi = {
  async list(): Promise<CalendarEvent[]> {
    const { data } = await apiClient.get("/api/auth/events");
    return data.events;
  },

  async create(input: CreateEventInput) {
    const { data } = await apiClient.post("/api/auth/events", input);
    return data;
  },

  async update(input: UpdateEventInput) {
    const { data } = await apiClient.put("/api/auth/events", input);
    return data;
  },

  async remove(eventId: string) {
    const { data } = await apiClient.delete("/api/auth/events", {
      data: { event_id: eventId }
    });
    return data;
  },

  async search(title: string, date?: string, day?: string) {
    const { data } = await apiClient.post("/api/auth/events/search", {
      title,
      date,
      day
    });
    return data;
  }
};
