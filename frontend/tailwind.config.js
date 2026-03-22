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
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        "sc-light": {
          "primary":   "#4A90D9",
          "secondary": "#6BA3BE",
          "accent":    "#F5A623",
          "base-100":  "#FFFFFF",
          "base-200":  "#F2F4F6",
        },
      },
      {
        "sc-dark": {
          "primary":   "#E2E8F0",
          "secondary": "#94A3B8",
          "accent":    "#F59E0B",
          "base-100":  "#1E293B",
          "base-200":  "#0F172A",
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
