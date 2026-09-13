import { forwardRef } from "react";
import { cn } from "@/lib/utils/cn";

export const Input = forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "h-11 w-full rounded-md border-3 border-ink bg-surface px-4 text-base placeholder:text-ink/40 focus-visible:outline-none focus-visible:ring-0",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";

export const Textarea = forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={cn(
      "w-full resize-none rounded-md border-3 border-ink bg-surface px-4 py-3 text-base placeholder:text-ink/40 focus-visible:outline-none",
      className
    )}
    {...props}
  />
));
Textarea.displayName = "Textarea";
