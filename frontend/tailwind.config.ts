import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Core dark navy palette
        navy: {
          950: "#0b0f19",
          900: "#0f1629",
          800: "#111827",
          700: "#1a2332",
          600: "#1f2937",
          500: "#283548",
          400: "#374151",
        },
        // Risk / Severity accent colors
        risk: {
          critical: "#ef4444",
          high: "#f59e0b",
          medium: "#3b82f6",
          low: "#10b981",
        },
        // Channel colors
        channel: {
          upi: "#8b5cf6",
          neft: "#06b6d4",
          imps: "#f97316",
          rtgs: "#ec4899",
        },
        // Surface colors
        surface: {
          DEFAULT: "#111827",
          raised: "#1a2332",
          overlay: "#1f2937",
        },
        // Accent / brand
        accent: {
          DEFAULT: "#6366f1",
          glow: "#818cf8",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Outfit", "Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      backgroundImage: {
        "glass-gradient":
          "linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)",
        "glow-gradient":
          "radial-gradient(ellipse at center, rgba(99,102,241,0.15) 0%, transparent 70%)",
        "card-gradient":
          "linear-gradient(180deg, rgba(26,35,50,0.8) 0%, rgba(17,24,39,0.95) 100%)",
      },
      boxShadow: {
        glass: "0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05)",
        "glass-sm": "0 4px 16px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.03)",
        glow: "0 0 20px rgba(99,102,241,0.3)",
        "glow-red": "0 0 20px rgba(239,68,68,0.3)",
        "glow-amber": "0 0 20px rgba(245,158,11,0.3)",
        "glow-emerald": "0 0 20px rgba(16,185,129,0.3)",
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
        "slide-in-right": "slideInRight 0.3s ease-out",
        shimmer: "shimmer 2s infinite linear",
        "pulse-glow": "pulseGlow 2s infinite",
        "spin-slow": "spin 3s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideInRight: {
          "0%": { opacity: "0", transform: "translateX(24px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        pulseGlow: {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};
export default config;
