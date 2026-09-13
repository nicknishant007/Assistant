/**
 * Type system.
 *
 * Display: "Space Grotesk" — the bold, slightly mechanical geometry that
 * reads on the reference boards (tight letterforms, blocky caps).
 * Body: "Inter" — kept neutral so long chat text and calendar data stay
 * legible at small sizes.
 */

export const fontFamily = {
  display: "var(--font-display)",
  body: "var(--font-body)"
} as const;

export const typeScale = {
  xs: "0.75rem",
  sm: "0.875rem",
  base: "1rem",
  lg: "1.125rem",
  xl: "1.5rem",
  "2xl": "2rem",
  "3xl": "2.75rem"
} as const;

export const fontWeight = {
  regular: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
  black: 800
} as const;
