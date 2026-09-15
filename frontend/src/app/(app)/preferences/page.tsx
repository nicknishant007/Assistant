import { AppShell } from "@/components/layout/AppShell";
import  {PreferencesForm}  from "@/components/preferences/PreferencesForm";

export default function PreferencesPage() {
  return (
    <AppShell rightPanel={false}>
      <div className="mx-auto w-full max-w-2xl space-y-6 p-6">
        <h1 className="font-display text-2xl font-black">Preferences</h1>
        <p className="text-sm text-ink/60">
          These control how the assistant schedules things on your behalf —
          your working hours and default meeting length.
        </p>
        <PreferencesForm />
      </div>
    </AppShell>
  );
}