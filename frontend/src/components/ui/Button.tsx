import { forwardRef } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 font-display font-bold border-3 border-ink rounded-md transition-transform active:translate-x-[2px] active:translate-y-[2px] active:shadow-pressed disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        primary: "bg-cobalt text-white shadow-md",
        secondary: "bg-surface text-ink shadow-md",
        mint: "bg-mint text-ink shadow-md",
        pink: "bg-pink text-ink shadow-md",
        ghost: "border-transparent shadow-none hover:bg-ink/5",
        danger: "bg-danger text-white shadow-md"
      },
      size: {
        sm: "h-9 px-3 text-sm",
        md: "h-11 px-5 text-base",
        lg: "h-14 px-7 text-lg"
      }
    },
    defaultVariants: { variant: "primary", size: "md" }
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    />
  )
);
Button.displayName = "Button";
