import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Volume2 } from "lucide-react";
import type { ChatMessage } from "@/types";
import { cn } from "@/lib/utils/cn";
import { formatMessageTime } from "@/lib/utils/date";
import { IconButton } from "@/components/ui/IconButton";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}>
      <div className={cn("flex max-w-[75ch] flex-col gap-1", isUser ? "items-end" : "items-start")}>
        <div
          className={cn(
            "rounded-lg border-3 border-ink px-4 py-3 shadow-sm",
            isUser ? "bg-pink" : "bg-surface"
          )}
        >
          <div className="prose prose-sm max-w-none prose-p:my-2 prose-pre:bg-ink prose-pre:text-paper">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          </div>
        </div>
        <div className="flex items-center gap-2 px-1 text-xs text-ink/50">
          <span>{formatMessageTime(message.createdAt)}</span>
          {message.audioUrl && (
            <IconButton
              aria-label="Play voice response"
              className="h-6 w-6"
              onClick={() => new Audio(message.audioUrl!).play()}
            >
              <Volume2 size={12} />
            </IconButton>
          )}
        </div>
      </div>
    </div>
  );
}
