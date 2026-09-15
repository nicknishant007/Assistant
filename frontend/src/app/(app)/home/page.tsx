"use client";

import { useRouter } from "next/navigation";
import { HomeHeader } from "@/components/layout/HomeHeader";
import { Button } from "@/components/ui/Button";
import { useAuthStore } from "@/store/authStore";

/**
 * Landing page after login. Deliberately does NOT use AppShell — no left
 * sidebar, no right context panel, per requirement 2.
 */
export default function HomePage() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);

  return (
    <div className="flex h-dvh w-full flex-col bg-paper">
      <HomeHeader />

      <main className="flex flex-1 flex-col items-center justify-center gap-6 p-6 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-lg border-3 border-ink bg-cobalt shadow-md">
          <span className="font-display text-2xl font-black text-white">N</span>
        </div>

        <div>
          <h1 className="font-display text-3xl font-black">
            Welcome{user?.name ? `, ${user.name}` : ""}
          </h1>
          <p className="mt-2 max-w-md text-sm text-ink/70">
            NuroFlow is your AI executive assistant. Chat to schedule,
            reschedule, or check your calendar — by text or voice.
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-3">
          <Button size="lg" onClick={() => router.push("/chat")}>
            Start chatting
          </Button>
          <Button variant="secondary" size="lg" onClick={() => router.push("/calendar")}>
            View calendar
          </Button>
          <Button variant="secondary" size="lg" onClick={() => router.push("/preferences")}>
            Manage preferences
          </Button>
        </div>
      </main>
    </div>
  );
}