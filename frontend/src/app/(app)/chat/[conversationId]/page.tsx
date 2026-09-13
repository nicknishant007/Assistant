"use client";

import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { useConversationStore } from "@/store/conversationStore";
import { useEffect } from "react";

export default function ConversationPage() {
  const { conversationId } = useParams<{ conversationId: string }>();
  const setActive = useConversationStore((s) => s.setActive);

  useEffect(() => {
    setActive(conversationId);
    return () => setActive(null);
  }, [conversationId, setActive]);

  return (
    <AppShell>
      <ChatWindow conversationId={conversationId} />
    </AppShell>
  );
}
