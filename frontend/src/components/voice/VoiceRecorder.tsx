"use client";

import { Mic, Square, X, Loader2 } from "lucide-react";
import { useVoiceStore } from "@/store/voiceStore";
import { IconButton } from "@/components/ui/IconButton";
import { cn } from "@/lib/utils/cn";

/**
 * Lives inline in ChatInput. Renders a waveform-style bar animation while
 * recording (CSS-only — no analyser node needed for the visual) and swaps
 * to a spinner while the backend transcribes + responds.
 */
export function VoiceRecorder({
  conversationId,
  onSent
}: {
  conversationId?: string | null;
  onSent?: (conversationId?: string) => void;
}) {
  const { recordingState, startRecording, stopRecording, cancelRecording, sendRecording, error } =
    useVoiceStore();

  if (recordingState === "idle") {
    return (
      <IconButton aria-label="Start voice recording" tone="mint" onClick={startRecording}>
        <Mic size={18} />
      </IconButton>
    );
  }

  if (recordingState === "recording") {
    return (
      <div className="flex items-center gap-2 rounded-md border-3 border-ink bg-pink px-3 py-1.5 shadow-sm">
        <div className="flex items-end gap-0.5" aria-hidden>
          {[6, 12, 8, 14, 5].map((h, i) => (
            <span
              key={i}
              className="w-1 animate-pulse rounded-full bg-ink"
              style={{ height: h, animationDelay: `${i * 100}ms` }}
            />
          ))}
        </div>
        <button
          aria-label="Cancel recording"
          onClick={cancelRecording}
          className="text-ink/70 hover:text-danger"
        >
          <X size={16} />
        </button>
        <button
          aria-label="Stop and send recording"
          onClick={async () => {
            const blob = await stopRecording();
            if (blob) {
              const result = await sendRecording(blob, conversationId ?? null);
              onSent?.(result?.conversationId);
            }
          }}
          className="text-ink"
        >
          <Square size={16} />
        </button>
      </div>
    );
  }

  if (recordingState === "processing") {
    return (
      <div className="flex items-center gap-2 rounded-md border-3 border-ink bg-surface px-3 py-1.5 text-sm shadow-sm">
        <Loader2 size={16} className="animate-spin" />
        Processing…
      </div>
    );
  }

  // error
  return (
    <div className="flex items-center gap-2 rounded-md border-3 border-ink bg-surface px-3 py-1.5 text-sm text-danger shadow-sm">
      {error ?? "Voice failed."}
      <button onClick={startRecording} className="underline">
        Retry
      </button>
    </div>
  );
}