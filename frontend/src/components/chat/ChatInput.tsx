"use client";

import { useRef, useState } from "react";
import { Send } from "lucide-react";
import { Textarea } from "@/components/ui/Input";
import { IconButton } from "@/components/ui/IconButton";
import { VoiceRecorder } from "@/components/voice/VoiceRecorder";

export function ChatInput({
  onSend,
  onVoiceSent,
  disabled,
  conversationId
}: {
  onSend: (text: string) => void;
  onVoiceSent?: (conversationId?: string) => void;
  disabled?: boolean;
  conversationId?: string | null;
}) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function submit() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    textareaRef.current?.focus();
  }

  return (
    <div className="border-t-3 border-ink bg-paper p-3 sm:p-4">
      <div className="mx-auto flex max-w-3xl items-end gap-2 rounded-lg border-3 border-ink bg-surface p-2 shadow-md">
        <Textarea
          ref={textareaRef}
          rows={1}
          value={value}
          placeholder="Ask NuroFlow to schedule, reschedule, or find something…"
          className="max-h-40 min-h-[44px] border-none shadow-none focus-visible:outline-none"
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
        />
        <VoiceRecorder conversationId={conversationId} onSent={onVoiceSent} />
        <IconButton
          aria-label="Send message"
          tone="mint"
          disabled={disabled || value.trim().length === 0}
          onClick={submit}
        >
          <Send size={18} />
        </IconButton>
      </div>
      <p className="mx-auto mt-2 max-w-3xl px-1 text-xs text-ink/50">
        Enter to send · Shift+Enter for a new line
      </p>
    </div>
  );
}