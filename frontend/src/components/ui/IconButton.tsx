import { forwardRef } from "react";
import { cn } from "@/lib/utils/cn";

interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  tone?: "surface" | "mint" | "pink" | "yellow";
  "aria-label": string;
}

const toneClass: Record<NonNullable<IconButtonProps["tone"]>, string> = {
  surface: "bg-surface",
  mint: "bg-mint",
  pink: "bg-pink",
  yellow: "bg-yellow"
};

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ className, tone = "surface", ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "flex h-10 w-10 items-center justify-center rounded-md border-3 border-ink shadow-sm transition-transform active:translate-x-[1px] active:translate-y-[1px] active:shadow-none disabled:opacity-40",
        toneClass[tone],
        className
      )}
      {...props}
    />
  )
);
IconButton.displayName = "IconButton";
