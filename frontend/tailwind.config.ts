import type { Config } from 'tailwindcss'

export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          DEFAULT: '#C9A84C',
          light: '#E2C97E',
          dark: '#A07830',
        },
        dark: {
          DEFAULT: '#0F0F0F',
          card: '#1A1A1A',
          hover: '#222222',
          border: '#2A2A2A',
        },
        text: {
          primary: '#F5F5F5',
          secondary: '#999999',
          muted: '#666666',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans JP', 'sans-serif'],
        mono: ['DM Mono', 'monospace'],
        jp: ['Noto Sans JP', 'sans-serif'],
      },
      backgroundImage: {
        'feather-watermark': "url('/feather-watermark.svg')",
      },
    },
  },
  plugins: [],
} satisfies Config
