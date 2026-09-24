"use client";

import { useRouter } from "next/navigation";
import { Calendar, MessageSquare, Mic, Sparkles } from "lucide-react";
import { HomeHeader } from "@/components/layout/HomeHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useAuthStore } from "@/store/authStore";
import { NotionConnectionCard } from "@/components/integrations/NotionConnectionCard";

const CAPABILITIES = [
  { icon: Calendar, text: "Check, create, move, or cancel events on your Google Calendar" },
  { icon: MessageSquare, text: "Search, read, and update pages in your connected Notion workspace" },
  { icon: Mic, text: "Talk instead of type — voice in, spoken reply back" },
  { icon: Sparkles, text: "Handles multi-step asks, like \"find my meeting tomorrow and push it an hour\"" }
];

/**
 * Landing page after login. Deliberately does NOT use AppShell — no left
 * sidebar, no right context panel, per requirement 2.
 */
export default function HomePage() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);

  return (
    <div className="flex h-dvh w-full flex-col overflow-y-auto bg-paper">
      <HomeHeader />

      <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col items-center gap-8 p-6 py-12 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-lg border-3 border-ink bg-cobalt shadow-md">
          <span className="font-display text-2xl font-black text-white">N</span>
        </div>

        <div>
          <h1 className="font-display text-3xl font-black">
            Welcome{user?.name ? `, ${user.name}` : ""}
          </h1>
          <p className="mx-auto mt-2 max-w-md text-sm text-ink/70">
            NuroFlow is your AI executive assistant. Chat to schedule,
            reschedule, or check your calendar — by text or voice.
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-3">
          <Button size="lg" className="bg-blue text-white hover:bg-mint" onClick={() => router.push("/chat")}>
            Start chatting
          </Button>
          <Button variant="secondary" size="lg" className="bg-blue text-white hover:bg-mint" onClick={() => router.push("/calendar")}>
            View calendar
          </Button>
          <Button variant="secondary" size="lg" className="bg-blue text-white hover:bg-mint" onClick={() => router.push("/preferences")}>
            Manage preferences
          </Button>
        </div>

        <Card tone="surface" className="w-full max-w-xl text-left">
          <h2 className="font-display text-lg font-bold">What NuroFlow can do</h2>
          <ul className="mt-3 space-y-2.5">
            {CAPABILITIES.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-start gap-3 text-sm text-ink/80">
                <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md border-2 border-ink bg-mint">
                  <Icon size={13} />
                </span>
                {text}
              </li>
            ))}
          </ul>
        </Card>

        <div className="w-full max-w-xl space-y-3 text-left">
          <h2 className="px-1 font-display text-lg font-bold">Integrations</h2>

          <Card tone="surface" className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold">Google Calendar</p>
              <p className="text-xs text-ink/60">Connected automatically when you log in</p>
            </div>
            <span className="rounded-pill border-2 border-ink bg-mint px-3 py-1 text-xs font-semibold">
              Connected
            </span>
          </Card>

          <NotionConnectionCard />
        </div>
      </main>
    </div>
  );
}