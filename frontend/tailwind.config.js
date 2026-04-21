/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#FAF9F6",
        surface: "#FFFFFF",
        primary: {
          DEFAULT: "#1B3B36",
          light: "#2A5C55",
          muted: "#EAF0EF",
        },
        text: {
          main: "#2D3748",
          muted: "#718096",
          light: "#A0AEC0",
        },
        accent: {
          sage: "#7C9A92",
          sand: "#C9B99A",
          blush: "#E8D5C4",
        },
        border: {
          light: "#E8E8E4",
          DEFAULT: "#D1D1CB",
        },
      },
      fontFamily: {
        serif: ["Playfair Display", "Georgia", "ui-serif", "serif"],
        sans: ["Inter", "Helvetica Neue", "system-ui", "sans-serif"],
      },
      fontSize: {
        "display-xl": ["4.5rem", { lineHeight: "1.1", letterSpacing: "-0.03em" }],
        "display-lg": ["3.5rem", { lineHeight: "1.15", letterSpacing: "-0.02em" }],
        "display-md": ["2.5rem", { lineHeight: "1.2", letterSpacing: "-0.02em" }],
      },
      boxShadow: {
        soft: "0 4px 20px rgba(0,0,0,0.05)",
        card: "0 2px 12px rgba(0,0,0,0.06)",
        elevated: "0 8px 40px rgba(0,0,0,0.08)",
      },
      borderRadius: {
        "4xl": "2rem",
        "5xl": "2.5rem",
      },
      spacing: {
        18: "4.5rem",
        22: "5.5rem",
      },
      animation: {
        "fade-up": "fadeUp 0.4s ease-out forwards",
        "fade-in": "fadeIn 0.3s ease-out forwards",
        "shimmer": "shimmer 2s infinite linear",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
  plugins: [],
}
