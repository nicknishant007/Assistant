import { create } from "zustand";
import { calendarApi } from "@/lib/api/calendar";
import type { CalendarEvent, CreateEventInput, UpdateEventInput } from "@/types";

type ViewMode = "month" | "week" | "day" | "agenda";

interface CalendarState {
  events: CalendarEvent[];
  loading: boolean;
  view: ViewMode;
  selectedEventId: string | null;
  isDrawerOpen: boolean;
  isCreateModalOpen: boolean;
  error: string | null;

  fetchEvents: () => Promise<void>;
  createEvent: (input: CreateEventInput) => Promise<void>;
  updateEvent: (input: UpdateEventInput) => Promise<void>;
  deleteEvent: (eventId: string) => Promise<void>;

  setView: (view: ViewMode) => void;
  openEvent: (eventId: string) => void;
  closeDrawer: () => void;
  openCreateModal: () => void;
  closeCreateModal: () => void;
}

export const useCalendarStore = create<CalendarState>((set, get) => ({
  events: [],
  loading: false,
  view: "month",
  selectedEventId: null,
  isDrawerOpen: false,
  isCreateModalOpen: false,
  error: null,

  fetchEvents: async () => {
    set({ loading: true, error: null });
    try {
      const events = await calendarApi.list();
      set({ events, loading: false });
    } catch (err) {
      set({
        loading: false,
        error: err instanceof Error ? err.message : "Could not load events."
      });
    }
  },

  createEvent: async (input) => {
    const created = await calendarApi.create(input);
    set((s) => ({ events: [...s.events, created], isCreateModalOpen: false }));
  },

  updateEvent: async (input) => {
    const updated = await calendarApi.update(input);
    set((s) => ({
      events: s.events.map((e) => (e.event_id === input.event_id ? updated : e))
    }));
  },

  deleteEvent: async (eventId) => {
    await calendarApi.remove(eventId);
    set((s) => ({
      events: s.events.filter((e) => e.event_id !== eventId),
      isDrawerOpen: false,
      selectedEventId: null
    }));
  },

  setView: (view) => set({ view }),
  openEvent: (eventId) => set({ selectedEventId: eventId, isDrawerOpen: true }),
  closeDrawer: () => set({ isDrawerOpen: false, selectedEventId: null }),
  openCreateModal: () => set({ isCreateModalOpen: true }),
  closeCreateModal: () => set({ isCreateModalOpen: false })
}));
