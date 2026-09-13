"use client";

import { useEffect } from "react";
import { ChevronsRight, ChevronsLeft, Clock } from "lucide-react";
import { useCalendarStore } from "@/store/calendarStore";
import { useUiStore } from "@/store/uiStore";
import { Card } from "@/components/ui/Card";
import { IconButton } from "@/components/ui/IconButton";
import { Badge } from "@/components/ui/Badge";
import { formatEventRange } from "@/lib/utils/date";
import { cn } from "@/lib/utils/cn";

/**
 * Right-hand "what's going on" panel: today's events + a live read on the
 * agent's current workflow. Collapsible on desktop, hidden entirely on
 * mobile (AppShell decides that) rather than trying to squeeze a third
 * column into a small viewport.
 */
export function ContextPanel({ workflowStatus }: { workflowStatus?: string | null }) {
  const { events, fetchEvents } = useCalendarStore();
  const { contextPanelCollapsed, toggleContextPanel } = useUiStore();

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const today = new Date().toDateString();
  const todaysEvents = events.filter(
    (e) => new Date(e.start_time).toDateString() === today
  );

  if (contextPanelCollapsed) {
    return (
      <div className="flex h-full w-12 flex-col items-center border-l-3 border-ink bg-paper py-4">
        <IconButton aria-label="Expand context panel" onClick={toggleContextPanel}>
          <ChevronsLeft size={16} />
        </IconButton>
      </div>
    );
  }

  return (
    <aside className="flex h-full w-80 flex-col gap-4 overflow-y-auto border-l-3 border-ink bg-paper p-4">
      <div className="flex items-center justify-between">
        <h2 className="font-display text-lg font-bold">Today</h2>
        <IconButton aria-label="Collapse context panel" onClick={toggleContextPanel}>
          <ChevronsRight size={16} />
        </IconButton>
      </div>

      {workflowStatus && (
        <Card tone="yellow" className="text-sm">
          <p className="font-semibold">Workflow in progress</p>
          <p className="mt-1 text-ink/80">{workflowStatus}</p>
        </Card>
      )}

      <div className="space-y-2">
        {todaysEvents.length === 0 && (
          <p className="text-sm text-ink/60">Nothing scheduled today.</p>
        )}
        {todaysEvents.map((event) => (
          <Card key={event.event_id} tone="surface" className="p-3">
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm font-semibold">{event.title}</p>
              <Badge tone="mint" className="shrink-0">
                <Clock size={12} />
              </Badge>
            </div>
            <p className="mt-1 text-xs text-ink/60">
              {formatEventRange(event.start_time, event.end_time)}
            </p>
          </Card>
        ))}
      </div>

      <div>
        <h3 className="mb-2 font-display text-sm font-bold uppercase text-ink/70">
          Upcoming
        </h3>
        <div className="space-y-2">
          {events
            .filter((e) => new Date(e.start_time).toDateString() !== today)
            .slice(0, 5)
            .map((event) => (
              <div
                key={event.event_id}
                className={cn("flex items-center justify-between rounded-md border-2 border-ink/20 px-3 py-2 text-xs")}
              >
                <span className="truncate">{event.title}</span>
                <span className="shrink-0 text-ink/50">
                  {new Date(event.start_time).toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric"
                  })}
                </span>
              </div>
            ))}
        </div>
      </div>
    </aside>
  );
}
