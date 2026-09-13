"use client";

import { Trash2 } from "lucide-react";
import { useCalendarStore } from "@/store/calendarStore";
import { Drawer } from "@/components/ui/Drawer";
import { Button } from "@/components/ui/Button";
import { formatEventRange } from "@/lib/utils/date";

export function EventDrawer() {
  const { events, selectedEventId, isDrawerOpen, closeDrawer, deleteEvent } =
    useCalendarStore();
  const event = events.find((e) => e.event_id === selectedEventId);

  return (
    <Drawer open={isDrawerOpen} onClose={closeDrawer} title="Event details">
      {event ? (
        <div className="space-y-4">
          <div>
            <p className="font-display text-xl font-bold">{event.title}</p>
            <p className="mt-1 text-sm text-ink/60">
              {formatEventRange(event.start_time, event.end_time)}
            </p>
          </div>
          <Button
            variant="danger"
            size="sm"
            onClick={() => deleteEvent(event.event_id)}
          >
            <Trash2 size={16} /> Delete event
          </Button>
        </div>
      ) : (
        <p className="text-sm text-ink/60">Select an event to see details.</p>
      )}
    </Drawer>
  );
}
