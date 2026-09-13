/**
 * Hard, offset "block" shadows (no blur) — the signature of the
 * reference boards. Kept as a token so a future re-theme can swap these
 * for soft shadows without touching component code.
 */
export const shadows = {
  none: "none",
  sm: "3px 3px 0 0 var(--color-ink)",
  md: "5px 5px 0 0 var(--color-ink)",
  lg: "8px 8px 0 0 var(--color-ink)",
  pressed: "2px 2px 0 0 var(--color-ink)"
} as const;
