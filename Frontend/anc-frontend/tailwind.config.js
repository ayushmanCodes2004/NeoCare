/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', 'sans-serif'],
        display: ['"Syne"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        navy: { 
          950: '#050d1a', 
          900: '#0a1628', 
          800: '#0f2044', 
          700: '#1a3560', 
          600: '#234a80' 
        },
        teal: { 
          400: '#2dd4bf', 
          500: '#14b8a6', 
          600: '#0d9488' 
        },
        risk: {
          critical: '#ef4444',
          high: '#f97316',
          medium: '#eab308',
          low: '#22c55e',
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.4s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: { 
          from: { opacity: 0 }, 
          to: { opacity: 1 } 
        },
        slideUp: { 
          from: { opacity: 0, transform: 'translateY(12px)' }, 
          to: { opacity: 1, transform: 'translateY(0)' } 
        },
      },
    },
  },
  plugins: [],
};
