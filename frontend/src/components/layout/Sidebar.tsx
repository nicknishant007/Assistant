"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { Plus, MessageSquare, Calendar, Settings, LogOut, Search, X } from "lucide-react";
import { useConversationStore } from "@/store/conversationStore";
import { useAuthStore } from "@/store/authStore";
import { useUiStore } from "@/store/uiStore";
import { IconButton } from "@/components/ui/IconButton";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils/cn";
import { formatConversationDate } from "@/lib/utils/date";

/**
 * Sidebar is a single component used both as the fixed desktop rail and
 * the mobile drawer body (see AppShell) — the responsive behavior lives
 * in AppShell, not duplicated here.
 */
export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { conversations, searchQuery, setSearchQuery, fetchAll, remove, activeId } =
    useConversationStore();
  const { logout, user } = useAuthStore();
  const setSidebarOpen = useUiStore((s) => s.setSidebarOpen);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const filtered = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <aside className="flex h-full w-full flex-col bg-mint">
      <div className="flex items-center justify-between border-b-3 border-ink p-4">
        <span className="font-display text-xl font-black tracking-tight">
          NuroFlow
        </span>
        <IconButton
          aria-label="Close menu"
          className="lg:hidden"
          onClick={() => setSidebarOpen(false)}
        >
          <X size={18} />
        </IconButton>
      </div>

      <div className="p-4">
        <Button
          variant="primary"
          className="w-full"
          onClick={() => {
            router.push("/chat");
            setSidebarOpen(false);
          }}
        >
          <Plus size={18} /> New chat
        </Button>
      </div>

      <div className="px-4 pb-2">
        <div className="relative">
          <Search
            size={16}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink/50"
          />
          <Input
            placeholder="Search conversations"
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-4 pb-2">
        {filtered.length === 0 && (
          <p className="mt-6 text-center text-sm text-ink/60">
            {searchQuery ? "No conversations match." : "No conversations yet — start one above."}
          </p>
        )}
        <ul className="space-y-2">
          {filtered.map((conversation) => {
            const isActive = activeId === conversation.id || pathname?.includes(conversation.id);
            return (
              <li key={conversation.id}>
                <Link
                  href={`/chat/${conversation.id}`}
                  onClick={() => setSidebarOpen(false)}
                  className={cn(
                    "group flex items-center justify-between gap-2 rounded-md border-3 border-transparent px-3 py-2 text-sm hover:border-ink",
                    isActive && "border-ink bg-surface shadow-sm"
                  )}
                >
                  <span className="flex min-w-0 items-center gap-2">
                    <MessageSquare size={16} className="shrink-0" />
                    <span className="truncate">{conversation.title}</span>
                  </span>
                  <span className="flex shrink-0 items-center gap-2">
                    <span className="text-xs text-ink/50">
                      {formatConversationDate(conversation.updatedAt)}
                    </span>
                    <button
                      aria-label={`Delete ${conversation.title}`}
                      className="hidden text-ink/50 hover:text-danger group-hover:block"
                      onClick={(e) => {
                        e.preventDefault();
                        remove(conversation.id);
                      }}
                    >
                      <X size={14} />
                    </button>
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="space-y-1 border-t-3 border-ink p-4">
        <SidebarLink href="/calendar" icon={<Calendar size={18} />} label="Calendar" active={pathname === "/calendar"} />
        <SidebarLink href="/settings" icon={<Settings size={18} />} label="Settings" active={pathname === "/settings"} />
        <button
          onClick={() => logout()}
          className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium hover:bg-ink/5"
        >
          <LogOut size={18} /> Log out {user ? `(${user.email})` : ""}
        </button>
      </div>
    </aside>
  );
}

function SidebarLink({
  href,
  icon,
  label,
  active
}: {
  href: string;
  icon: React.ReactNode;
  label: string;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium hover:bg-ink/5",
        active && "bg-surface border-3 border-ink shadow-sm"
      )}
    >
      {icon}
      {label}
    </Link>
  );
}
