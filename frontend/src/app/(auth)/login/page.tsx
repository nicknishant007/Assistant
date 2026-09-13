"use client";

import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

/**
 * Backend only supports Google OAuth (Backend/api/routes/auth.py has no
 * password endpoint), so this is a single call-to-action screen rather
 * than a form. If email/password auth is added later, this is the only
 * file that needs a new branch.
 */
export default function LoginPage() {
  const loginWithGoogle = useAuthStore((s) => s.loginWithGoogle);

  return (
    <div className="flex min-h-dvh items-center justify-center bg-paper p-4">
      <Card tone="mint" className="w-full max-w-sm text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-lg border-3 border-ink bg-cobalt shadow-sm">
          <span className="font-display text-2xl font-black text-white">N</span>
        </div>
        <h1 className="font-display text-2xl font-black">NuroFlow</h1>
        <p className="mt-2 text-sm text-ink/70">
          Your AI executive assistant for chat, scheduling, and your calendar.
        </p>
        <Button className="mt-6 w-full" onClick={loginWithGoogle}>
          Continue with Google
        </Button>
      </Card>
    </div>
  );
}
