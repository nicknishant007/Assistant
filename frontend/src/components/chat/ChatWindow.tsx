"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useChatStore } from "@/store/chatStore";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import { ChatInput } from "./ChatInput";
import { Card } from "@/components/ui/Card";

export function ChatWindow({ conversationId }: { conversationId: string | null }) {
  const router = useRouter();
  const { messagesFor, sendMessage, isAssistantTyping, error } = useChatStore();
  const messages = messagesFor(conversationId ?? "__draft__");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, isAssistantTyping]);

  async function handleSend(text: string) {
    const { conversationId: resolvedId } = await sendMessage(conversationId, text);
    if (!conversationId) {
      router.push(`/chat/${resolvedId}`);
    }
  }

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="min-h-0 flex-1 overflow-y-auto">
        <div className="mx-auto flex max-w-3xl flex-col gap-4 p-4 sm:p-6">
          {messages.length === 0 && <EmptyState onSuggestion={handleSend} />}
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          {isAssistantTyping && <TypingIndicator />}
          {error && (
            <Card tone="pink" className="text-sm">
              {error}
            </Card>
          )}
          <div ref={bottomRef} />
        </div>
      </div>
      <ChatInput onSend={handleSend} disabled={isAssistantTyping} />
    </div>
  );
}

function EmptyState({ onSuggestion }: { onSuggestion: (text: string) => void }) {
  const suggestions = [
    "What's on my calendar today?",
    "Schedule a 30 minute gym session tomorrow morning",
    "Move my 3pm meeting to Friday at the same time"
  ];

  return (
    <div className="flex flex-1 flex-col items-center justify-center py-16 text-center">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-lg border-3 border-ink bg-cobalt shadow-md">
        <span className="font-display text-2xl font-black text-white">N</span>
      </div>
      <h1 className="font-display text-2xl font-black">What can I help with?</h1>
      <p className="mt-2 max-w-sm text-sm text-ink/60">
        Ask NuroFlow to check your schedule, book time, or move things around —
        by text or voice.
      </p>
      <div className="mt-6 flex flex-wrap justify-center gap-2">
        {suggestions.map((s) => (
          <button
            key={s}
            onClick={() => onSuggestion(s)}
            className="rounded-pill border-3 border-ink bg-surface px-4 py-2 text-sm font-medium shadow-sm hover:bg-mint"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
