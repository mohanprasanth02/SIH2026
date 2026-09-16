/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // SATQuery Light Design System
        sq: {
          bg: "#F6F7F4",
          bgSecondary: "#EEF0EC",
          surface: "#FFFFFF",
          surfaceHover: "#FAFAF9",
          border: "#DDE1DD",
          borderHover: "#CCD2CB",
          text: "#111516",
          textMuted: "#687277",
          textSubtle: "#9BA3A8",
          teal: "#0C7C72",
          tealHover: "#09635B",
          tealLight: "#E8F4F2",
          amber: "#D8893D",
          amberHover: "#C4772E",
          amberLight: "#FBF3EB",
          green: "#258A65",
          greenLight: "#EBF6F1",
          red: "#C84B4B",
          redLight: "#FBEFEF",
          mapAccent: "#168B82",
        },
        // Land cover natural palette
        lc: {
          water: "#168B82",
          vegetation: "#258A65",
          agriculture: "#D8893D",
          buildup: "#C84B4B",
          roads: "#5A676D",
          bareland: "#BFA07A",
          forest: "#1A5E44",
          wetland: "#3B9C94",
          other: "#8C969B",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        display: ["Manrope", "Inter", "sans-serif"],
        heading: ["Manrope", "Inter", "sans-serif"],
        mono: ["'JetBrains Mono'", "'IBM Plex Mono'", "monospace"],
      },
      borderRadius: {
        DEFAULT: "8px",
        sm: "6px",
        md: "8px",
        lg: "12px",
        xl: "14px",
        "2xl": "16px",
        full: "9999px",
      },
      boxShadow: {
        card: "0 1px 3px rgba(17, 21, 22, 0.02), 0 4px 12px rgba(17, 21, 22, 0.03)",
        floating: "0 2px 8px -2px rgba(17, 21, 22, 0.04), 0 8px 24px -4px rgba(17, 21, 22, 0.06)",
        elevated: "0 12px 36px -4px rgba(17, 21, 22, 0.08)",
        toolbar: "0 4px 16px -2px rgba(17, 21, 22, 0.06), 0 1px 3px rgba(17, 21, 22, 0.03)",
      },
      animation: {
        "fade-in": "fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)",
        "slide-up": "slideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1)",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(8px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
      },
    },
  },
  plugins: [],
}
