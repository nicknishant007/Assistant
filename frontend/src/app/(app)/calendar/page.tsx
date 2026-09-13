import { AppShell } from "@/components/layout/AppShell";
import { CalendarView } from "@/components/calendar/CalendarView";

export default function CalendarPage() {
  return (
    <AppShell rightPanel={false}>
      <CalendarView />
    </AppShell>
  );
}
