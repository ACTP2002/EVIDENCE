/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0A2540',
          light: '#1A3F5F',
        },
        accent: {
          DEFAULT: '#00D4FF',
          hover: '#00B8E0',
        },
        risk: {
          critical: '#DC2626',
          high: '#EA580C',
          medium: '#F59E0B',
          low: '#10B981',
        },
        status: {
          open: '#3B82F6',
          confirmed: '#DC2626',
          false: '#10B981',
          review: '#F59E0B',
        },
      },
      fontFamily: {
        sans: ['DM Sans', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        sm: '6px',
        md: '8px',
        lg: '12px',
      },
    },
  },
  plugins: [],
}
