import { cn } from "@/lib/utils/cn";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  tone?: "mint" | "pink" | "yellow" | "cobalt" | "surface";
}

const toneClass: Record<NonNullable<BadgeProps["tone"]>, string> = {
  mint: "bg-mint text-ink",
  pink: "bg-pink text-ink",
  yellow: "bg-yellow text-ink",
  cobalt: "bg-cobalt text-white",
  surface: "bg-surface text-ink"
};

export function Badge({ className, tone = "surface", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-pill border-2 border-ink px-3 py-1 text-xs font-semibold",
        toneClass[tone],
        className
      )}
      {...props}
    />
  );
}
