/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'senior-blue': '#1E40AF',
        'senior-orange': '#EA580C',
        'nana-warm': '#C2410C',
        'nana-ink': '#7C2D12',
        'nana-bg': '#FFF7ED',
      }
    },
  },
  plugins: [],
}
