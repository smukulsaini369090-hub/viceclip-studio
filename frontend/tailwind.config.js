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
          950: "#08090B", // Deepest viewport canvas & rail
          900: "#0B0C0E", // Page background
          850: "#0E1013", // Secondary background
          800: "#111317", // Card surface
          750: "#14171D", // Card hover
          700: "#181B20", // Raised input & active row
          600: "#22262E", // Hairline border
          500: "#2D323E", // Focused border
          400: "#626875", // Muted text & metadata
          300: "#959CA8", // Secondary text
          200: "#CBD0D8", // Body text
          100: "#ECEFF4", // Primary high-contrast text
        },
        tally: {
          amber: "#F59E0B",
          emerald: "#10B981",
          red: "#EF4444",
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
        "studio-card": "0 1px 3px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.04)",
        "studio-raised": "0 2px 6px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08)",
      },
      animation: {
        "pulse-subtle": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
};
