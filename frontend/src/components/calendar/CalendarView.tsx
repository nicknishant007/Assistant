"use client";

import { useEffect, useMemo } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import { Plus } from "lucide-react";
import { useCalendarStore } from "@/store/calendarStore";
import { Button } from "@/components/ui/Button";
import { EventDrawer } from "./EventDrawer";
import { CreateEventModal } from "./CreateEventModal";

/**
 * FullCalendar is themed entirely through CSS variables in globals.css
 * (see the `.fc` overrides there) rather than FullCalendar's own theme
 * system, so it inherits re-brands automatically.
 */
export function CalendarView() {
  const { events, fetchEvents, openEvent, openCreateModal, loading } = useCalendarStore();

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const calendarEvents = useMemo(
    () =>
      events.map((e) => ({
        id: e.event_id,
        title: e.title,
        start: e.start_time,
        end: e.end_time
      })),
    [events]
  );

  return (
    <div className="flex h-full flex-col gap-4 p-4 sm:p-6">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl font-black">Calendar</h1>
        <Button onClick={openCreateModal}>
          <Plus size={18} /> New event
        </Button>
      </div>

      <div className="min-h-0 flex-1 overflow-auto rounded-lg border-3 border-ink bg-surface p-2 shadow-md">
        <FullCalendar
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="dayGridMonth"
          headerToolbar={{
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek,timeGridDay"
          }}
          height="100%"
          events={calendarEvents}
          eventClick={(info) => openEvent(info.event.id)}
        />
      </div>

      {loading && <p className="text-sm text-ink/60">Loading events…</p>}

      <EventDrawer />
      <CreateEventModal />
    </div>
  );
}
