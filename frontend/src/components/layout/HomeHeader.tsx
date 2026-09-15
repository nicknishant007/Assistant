"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { User as UserIcon, LogOut, SlidersHorizontal } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { IconButton } from "@/components/ui/IconButton";

/**
 * Header used only on the Home page (no sidebar/context panel there).
 * Logo returns to /home; the avatar opens a small menu to Profile,
 * Preferences, and Logout — the nav surface requirement 5 asks for.
 */
export function HomeHeader() {
  const router = useRouter();
  const { logout } = useAuthStore();
  const [menuOpen, setMenuOpen] = useState(false);

  async function handleLogout() {
    setMenuOpen(false);
    await logout();
    router.replace("/login");
  }

  return (
    <header className="flex items-center justify-between border-b-3 border-ink bg-paper px-4 py-3 sm:px-6">
      <Link href="/home" className="flex items-center gap-2">
        <div className="flex h-9 w-9 items-center justify-center rounded-md border-3 border-ink bg-cobalt shadow-sm">
          <span className="font-display text-lg font-black text-white">N</span>
        </div>
        <span className="font-display text-lg font-black tracking-tight">NuroFlow</span>
      </Link>

      <div className="relative">
        <IconButton
          aria-label="Open profile menu"
          tone="mint"
          onClick={() => setMenuOpen((v) => !v)}
        >
          <UserIcon size={18} />
        </IconButton>

        {menuOpen && (
          <div className="absolute right-0 top-12 z-20 w-48 rounded-md border-3 border-ink bg-surface p-2 shadow-md">
            <Link
              href="/profile"
              className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium hover:bg-ink/5"
              onClick={() => setMenuOpen(false)}
            >
              <UserIcon size={16} /> Profile
            </Link>
            <Link
              href="/preferences"
              className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium hover:bg-ink/5"
              onClick={() => setMenuOpen(false)}
            >
              <SlidersHorizontal size={16} /> Preferences
            </Link>
            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-danger hover:bg-ink/5"
            >
              <LogOut size={16} /> Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
}