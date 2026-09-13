/**
 * NuroFlow color tokens.
 *
 * Derived from the reference boards: a cream/mint workspace, ink-black
 * hairline borders, and three accent blocks (cobalt, pink, yellow) that
 * are used to differentiate *roles* in the UI (system/user/status), not
 * decoration. Nothing below is consumed directly by components — always
 * go through the Tailwind tokens in tailwind.config.ts or the CSS
 * variables in globals.css so a re-theme only ever touches this file.
 */

export const colors = {
  // Neutrals
  ink: "#14151A", // borders, primary text, icon strokes
  paper: "#F4EFDC", // app background (warm cream, not pure white)
  surface: "#FFFFFF", // card surfaces sitting on top of paper

  // Brand accents — each one owns a job, not just a shelf color
  mint: "#8FE3C8", // primary brand surface (sidebar, header)
  cobalt: "#3D3DE8", // primary action / assistant messages / links
  pink: "#F3A6C6", // user messages / highlights / destructive-adjacent accents
  yellow: "#F6D24C", // pending / approval / attention states

  // Status
  success: "#2FAE66",
  danger: "#E8543D",
  warning: "#F6D24C",
  info: "#3D3DE8"
} as const;

export type ColorToken = keyof typeof colors;
