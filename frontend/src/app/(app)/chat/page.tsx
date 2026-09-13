"use client";

import { AppShell } from "@/components/layout/AppShell";
import { ChatWindow } from "@/components/chat/ChatWindow";

/** /chat — no conversation yet; ChatWindow shows the empty state and
 *  creates a conversation as soon as the first message is sent. */
export default function NewChatPage() {
  return (
    <AppShell>
      <ChatWindow conversationId={null} />
    </AppShell>
  );
}
