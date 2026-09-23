"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Calendar as CalendarIcon } from "lucide-react";
import { useNotionStore } from "@/store/notionStore";
import { cn } from "@/lib/utils/cn";

/**
 * Small "which apps am I connected to" pill, pinned to the bottom-right
 * of the chat window, above the input bar. Calendar always shows
 * connected — Google OAuth is required just to log in, so there's no
 * disconnected state to represent here. Notion reflects the real
 * notionStore status. The whole pill links to Settings, where the
 * person can actually connect/disconnect Notion.
 */
export function IntegrationsStatusBar() {
  const { connected: notionConnected, checked, fetchStatus } = useNotionStore();

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  return (
    <div className="pointer-events-none absolute bottom-24 right-4 z-10 sm:bottom-28 sm:right-6">
      <Link
        href="/settings"
        className="pointer-events-auto flex items-center gap-2 rounded-pill border-3 border-ink bg-surface px-3 py-1.5 text-xs font-medium shadow-md transition-colors hover:bg-mint"
      >
        <span className="flex items-center gap-1.5" title="Google Calendar">
          <CalendarIcon size={13} />
          <span className="h-1.5 w-1.5 rounded-full bg-success" />
        </span>

        <span className="h-3 w-px bg-ink/20" />

        <span className="flex items-center gap-1.5" title="Notion">
          <NotionGlyph />
          <span
            className={cn(
              "h-1.5 w-1.5 rounded-full",
              checked && notionConnected ? "bg-success" : "bg-ink/30"
            )}
          />
        </span>
      </Link>
    </div>
  );
}

/** Notion has no lucide icon, so this is a minimal glyph matched to the
 *  stroke weight of the surrounding lucide icons. */
function NotionGlyph() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="3" width="18" height="18" rx="3" stroke="currentColor" strokeWidth="2" />
      <path
        d="M8 8v8M8 8l8 8M16 8v8"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}