/** @type {import('tailwindcss').Config} */
// Primary Tailwind + DaisyUI config is in src/style.css via @import "tailwindcss" and @plugin "daisyui".
// This file exists for tooling that expects tailwind.config.js; Tailwind v4 with @tailwindcss/vite uses CSS-first config.
import daisyui from 'daisyui'
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [daisyui],
}
