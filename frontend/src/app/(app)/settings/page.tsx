"use client";

import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/ui/Card";
import { useAuthStore } from "@/store/authStore";

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);

  return (
    <AppShell rightPanel={false}>
      <div className="mx-auto w-full max-w-2xl space-y-6 p-6">
        <h1 className="font-display text-2xl font-black">Settings</h1>
        <Card>
          <h2 className="font-display text-lg font-bold">Account</h2>
          <p className="mt-2 text-sm text-ink/70">{user?.email}</p>
        </Card>
        <Card tone="paper">
          <h2 className="font-display text-lg font-bold">Integrations</h2>
          <p className="mt-2 text-sm text-ink/70">
            Google Calendar is connected via OAuth on login (see
            Backend/services/integration_service.py). Reconnecting or
            revoking access from here would call a new
            /api/auth/integrations endpoint once the backend exposes one.
          </p>
        </Card>
      </div>
    </AppShell>
  );
}
