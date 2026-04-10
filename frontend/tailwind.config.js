/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'laflo-gold': '#D79922',
        'laflo-cream': '#EFE2BA',
        'laflo-coral': '#F13C20',
        'laflo-navy': '#4056A1',
        'laflo-periwinkle': '#C5CBE3',
      },
    },
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
  daisyui: {
    themes: [
      {
        "sc-light": {
          "primary":   "#4A90D9",
          "secondary": "#6BA3BE",
          "accent":    "#F5A623",
          "base-100":  "#FFFFFF",
          "base-200":  "#F2F4F6",
          "info":      "#BAE6FD",
          "info-content": "#0C4A6E",
          "success":   "#BBF7D0",
          "success-content": "#14532D",
          "warning":   "#FDE68A",
          "warning-content": "#78350F",
          "error":     "#FECACA",
          "error-content": "#7F1D1D",
        },
      },
      {
        "sc-dark": {
          "primary":   "#E2E8F0",
          "secondary": "#94A3B8",
          "accent":    "#F59E0B",
          "base-100":  "#1E293B",
          "base-200":  "#0F172A",
          "info":      "#1E3A5F",
          "info-content": "#93C5FD",
          "success":   "#14532D",
          "success-content": "#86EFAC",
          "warning":   "#78350F",
          "warning-content": "#FCD34D",
          "error":     "#7F1D1D",
          "error-content": "#FCA5A5",
        },
      },
      {
        storyCreator: {
          "primary": "#D79922",      // Gold - Main actions
          "secondary": "#EFE2BA",    // Cream - Backgrounds
          "accent": "#F13C20",       // Coral - GPT/emphasis
          "neutral": "#C5CBE3",      // Periwinkle - Borders
          "base-100": "#FFFFFF",     // White
          "base-200": "#EFE2BA",     // Cream
          "base-300": "#C5CBE3",     // Periwinkle
          "info": "#4056A1",         // Navy - Headers/links
          "success": "#36D399",
          "warning": "#FBBD23",
          "error": "#F87272",
        },
      },
    ],
  },
}
