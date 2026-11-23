/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        studio: {
          950: "#07070A",
          900: "#0A0A0F",
          850: "#0F0F15",
          800: "#121218",
          750: "#161620",
          700: "#1A1A24",
          600: "#242432",
          500: "#323244",
          400: "#505068",
          300: "#7E7E9A",
          200: "#B0B0C8",
          100: "#E2E2F0",
        },
        vice: {
          pink: "#FF2E93",
          cyan: "#00F0FF",
          yellow: "#FFE600",
          purple: "#9D00FF",
          dark: "#0A0A0F",
        },
      },
      fontFamily: {
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "Liberation Mono",
          "Courier New",
          "monospace",
        ],
      },
      boxShadow: {
        "neon-pink": "0 0 15px rgba(255, 46, 147, 0.35)",
        "neon-cyan": "0 0 15px rgba(0, 240, 255, 0.35)",
        "neon-yellow": "0 0 15px rgba(255, 230, 0, 0.35)",
        "studio-glow": "0 8px 32px rgba(0, 0, 0, 0.6)",
      },
      animation: {
        "pulse-subtle": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "scanner": "scan 2s linear infinite",
      },
      keyframes: {
        scan: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(1000%)" },
        },
      },
    },
  },
  plugins: [],
};
