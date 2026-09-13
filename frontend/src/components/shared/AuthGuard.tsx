"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { Loader2 } from "lucide-react";

/** Wraps every route under (app) — redirects to /login if the session
 *  cookie doesn't resolve to a user. */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { status, hydrate } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (status === "unauthenticated") router.replace("/login");
  }, [status, router]);

  if (status === "idle" || status === "loading") {
    return (
      <div className="flex h-dvh items-center justify-center bg-paper">
        <Loader2 className="animate-spin" />
      </div>
    );
  }

  if (status === "unauthenticated") return null;

  return <>{children}</>;
}
