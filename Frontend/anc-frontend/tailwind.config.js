/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // NeoSure Brand Colors
        primary: '#C4622D', // Alias for terra
        terra: {
          DEFAULT: '#C4622D',
          dark: '#9E4A1E',
          light: '#E8835A',
        },
        peach: {
          DEFAULT: '#F5E6D8',
          mid: '#EDD5BF',
        },
        cream: '#FAF4EE',
        warm: '#FEFBF7',
        brown: {
          dark: '#2C1A0E',
          mid: '#5C3A1E',
          muted: '#8C6B52',
        },
        // Risk Colors
        critical: '#dc2626',
        high: '#ea580c',
        medium: '#ca8a04',
        low: '#16a34a',
        // Status Colors
        green: {
          DEFAULT: '#3A7D5C',
          bg: '#E6F4ED',
        },
        amber: {
          DEFAULT: '#C4860A',
          bg: '#FFF4DC',
        },
        red: {
          DEFAULT: '#C03040',
          bg: '#FDEAEB',
        },
      },
      fontFamily: {
        sans: ['Jost', 'system-ui', 'sans-serif'],
        serif: ['Cormorant Garamond', 'Georgia', 'serif'],
      },
      animation: {
        'fade-up': 'fadeUp 0.7s ease both',
        'fade-in': 'fadeIn 0.5s ease both',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
