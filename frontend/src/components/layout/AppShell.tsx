"use client";

import { Menu } from "lucide-react";
import { Sidebar } from "./Sidebar";
import { ContextPanel } from "./ContextPanel";
import { useUiStore } from "@/store/uiStore";
import { IconButton } from "@/components/ui/IconButton";
import { cn } from "@/lib/utils/cn";

/**
 * Three-panel desktop layout that collapses to a single panel + drawer
 * on mobile, per the brief:
 *
 *   Desktop: [ Sidebar | Main | ContextPanel ]  (all three, fixed widths)
 *   Tablet:  [ (drawer)Sidebar | Main ]          (context panel hidden)
 *   Mobile:  [ Main ]                            (sidebar becomes a drawer)
 */
export function AppShell({
  children,
  rightPanel = true,
  workflowStatus
}: {
  children: React.ReactNode;
  rightPanel?: boolean;
  workflowStatus?: string | null;
}) {
  const { sidebarOpen, setSidebarOpen } = useUiStore();

  return (
    <div className="flex h-dvh w-full overflow-hidden bg-paper">
      {/* Desktop sidebar */}
      <div className="hidden lg:block lg:w-72 lg:shrink-0">
        <Sidebar />
      </div>

      {/* Mobile drawer */}
      <div
        className={cn(
          "fixed inset-0 z-40 lg:hidden",
          sidebarOpen ? "pointer-events-auto" : "pointer-events-none"
        )}
      >
        <div
          className={cn(
            "absolute inset-0 bg-ink/40 transition-opacity",
            sidebarOpen ? "opacity-100" : "opacity-0"
          )}
          onClick={() => setSidebarOpen(false)}
        />
        <div
          className={cn(
            "absolute inset-y-0 left-0 w-80 max-w-[85%] border-r-3 border-ink transition-transform",
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          )}
        >
          <Sidebar />
        </div>
      </div>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b-3 border-ink bg-paper p-3 lg:hidden">
          <IconButton aria-label="Open menu" onClick={() => setSidebarOpen(true)}>
            <Menu size={18} />
          </IconButton>
          <span className="font-display text-lg font-black">NuroFlow</span>
        </header>

        <div className="flex min-h-0 flex-1">
          <main className="flex min-w-0 flex-1 flex-col">{children}</main>

          {rightPanel && (
            <div className="hidden xl:block">
              <ContextPanel workflowStatus={workflowStatus} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
