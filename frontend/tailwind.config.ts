import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: {
          DEFAULT: "#0A0B0F",
          panel: "#101217",
          raised: "#15181F",
        },
        border: {
          subtle: "rgba(255,255,255,0.08)",
          hover: "rgba(255,255,255,0.16)",
        },
        accent: {
          DEFAULT: "#7C9CFF",
          soft: "#A9BEFF",
          teal: "#35D0BA",
          amber: "#F0A64B",
          rose: "#F0637C",
        },
        ink: {
          DEFAULT: "#E9EAEE",
          muted: "#9098A8",
          faint: "#5B616E",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(124,156,255,0.15), 0 8px 30px -8px rgba(124,156,255,0.35)",
        soft: "0 8px 30px -12px rgba(0,0,0,0.6)",
      },
      backgroundImage: {
        "grid-fade": "radial-gradient(circle at 50% 0%, rgba(124,156,255,0.08), transparent 60%)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "pop": {
          "0%": { transform: "scale(0.94)", opacity: "0" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        "pulse-glow": {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(124,156,255,0.35)" },
          "50%": { boxShadow: "0 0 0 8px rgba(124,156,255,0)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.35s ease-out",
        "pop": "pop 0.2s ease-out",
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
export default config;
