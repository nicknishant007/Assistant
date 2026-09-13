import { cn } from "@/lib/utils/cn";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  tone?: "surface" | "mint" | "pink" | "yellow" | "paper";
}

const toneClass: Record<NonNullable<CardProps["tone"]>, string> = {
  surface: "bg-surface",
  mint: "bg-mint",
  pink: "bg-pink",
  yellow: "bg-yellow",
  paper: "bg-paper"
};

export function Card({ className, tone = "surface", ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-lg border-3 border-ink shadow-md p-5",
        toneClass[tone],
        className
      )}
      {...props}
    />
  );
}
