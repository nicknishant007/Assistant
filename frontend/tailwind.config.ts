import type { Config } from "tailwindcss";

/**
 * Tailwind never hardcodes hex values here — every color/radius/shadow
 * resolves to a CSS variable defined in globals.css, which in turn is
 * generated from /src/theme/*.ts. To rebrand NuroFlow: edit /src/theme,
 * regenerate the CSS variables, done. No component changes needed.
 */
const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "var(--color-ink)",
        paper: "var(--color-paper)",
        surface: "var(--color-surface)",
        mint: "var(--color-mint)",
        cobalt: "var(--color-cobalt)",
        pink: "var(--color-pink)",
        yellow: "var(--color-yellow)",
        success: "var(--color-success)",
        danger: "var(--color-danger)",
        warning: "var(--color-warning)",
        info: "var(--color-info)"
      },
      fontFamily: {
        display: ["var(--font-display)"],
        body: ["var(--font-body)"]
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        xl: "var(--radius-xl)",
        pill: "var(--radius-pill)"
      },
      boxShadow: {
        sm: "var(--shadow-sm)",
        md: "var(--shadow-md)",
        lg: "var(--shadow-lg)",
        pressed: "var(--shadow-pressed)"
      },
      borderWidth: {
        DEFAULT: "1.5px",
        3: "3px"
      }
    }
  },
  plugins: []
};

export default config;
