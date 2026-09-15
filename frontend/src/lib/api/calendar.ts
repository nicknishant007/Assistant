import { apiClient } from "./client";
import type { CalendarEvent, CreateEventInput, UpdateEventInput } from "@/types";

/**
 * The backend's /api/auth/events* endpoints don't return our CalendarEvent
 * shape directly — they forward Google Calendar's raw event object
 * (id / summary / start.dateTime / end.dateTime), and create/update wrap
 * it as { success, event }. This normalizer maps either shape into
 * CalendarEvent so the rest of the frontend never has to know about it.
 */
function normalizeEvent(raw: any): CalendarEvent {
  return {
    event_id: raw.event_id ?? raw.id,
    title: raw.title ?? raw.summary ?? "(untitled)",
    start_time: raw.start_time ?? raw.start?.dateTime ?? raw.start?.date,
    end_time: raw.end_time ?? raw.end?.dateTime ?? raw.end?.date
  };
}

/**
 * Maps to Backend/api/routes/auth.py's /api/auth/events* endpoints
 * (calendar lives under the auth router today because event creation
 * needs the Google integration tied to the logged-in user).
 */
export const calendarApi = {
  async list(): Promise<CalendarEvent[]> {
    const { data } = await apiClient.get("/api/auth/events");
    return (data.events ?? []).map(normalizeEvent);
  },

  async create(input: CreateEventInput): Promise<CalendarEvent> {
    const { data } = await apiClient.post("/api/auth/events", input);
    return normalizeEvent(data.event ?? data);
  },

  async update(input: UpdateEventInput): Promise<CalendarEvent> {
    const { data } = await apiClient.put("/api/auth/events", input);
    return normalizeEvent(data.event ?? data);
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