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
