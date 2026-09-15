"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { usePreferencesStore } from "@/store/preferencesStore";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

// Backend stores time as "HH:MM:SS"; <input type="time"> wants "HH:MM".
function toInputTime(value: string | null): string {
  return value ? value.slice(0, 5) : "";
}

function toApiTime(value: string): string | undefined {
  if (!value) return undefined;
  return value.length === 5 ? `${value}:00` : value;
}

export function PreferencesForm() {
  const { preferences, loading, error, fetchPreferences, updatePreferences } =
    usePreferencesStore();

  const [wakeTime, setWakeTime] = useState("");
  const [sleepTime, setSleepTime] = useState("");
  const [workStartTime, setWorkStartTime] = useState("");
  const [focusDuration, setFocusDuration] = useState(60);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchPreferences();
  }, [fetchPreferences]);

  useEffect(() => {
    if (preferences) {
      setWakeTime(toInputTime(preferences.wake_time));
      setSleepTime(toInputTime(preferences.sleep_time));
      setWorkStartTime(toInputTime(preferences.work_start_time));
      setFocusDuration(preferences.focus_duration ?? 60);
    }
  }, [preferences]);

  async function handleSave() {
    setSaving(true);
    try {
      await updatePreferences({
        wake_time: toApiTime(wakeTime),
        sleep_time: toApiTime(sleepTime),
        work_start_time: toApiTime(workStartTime),
        focus_duration: focusDuration
      });
      toast.success("Preferences updated");
    } catch {
      toast.error("Couldn't update preferences");
    } finally {
      setSaving(false);
    }
  }

  if (loading && !preferences) {
    return <p className="text-sm text-ink/60">Loading preferences…</p>;
  }

  return (
    <Card className="max-w-lg space-y-4">
      {error && <p className="text-sm text-danger">{error}</p>}

      <div>
        <label className="mb-1 block text-sm font-medium">Wake time</label>
        <Input type="time" value={wakeTime} onChange={(e) => setWakeTime(e.target.value)} />
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Sleep time</label>
        <Input type="time" value={sleepTime} onChange={(e) => setSleepTime(e.target.value)} />
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Work start time</label>
        <Input
          type="time"
          value={workStartTime}
          onChange={(e) => setWorkStartTime(e.target.value)}
        />
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">
          Preferred meeting / focus duration (minutes)
        </label>
        <Input
          type="number"
          min={5}
          step={5}
          value={focusDuration}
          onChange={(e) => setFocusDuration(Number(e.target.value))}
        />
      </div>

      <Button onClick={handleSave} disabled={saving}>
        {saving ? "Saving…" : "Save changes"}
      </Button>
    </Card>
  );
}