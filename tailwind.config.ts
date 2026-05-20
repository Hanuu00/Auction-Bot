import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}', './components/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0D0D0D',
        surface: '#1A1A1A',
        primary: '#FF3D6B',
        secondary: '#FFD600',
        textPrimary: '#FFFFFF',
        textSecondary: '#A0A0B0',
        border: '#2E2E2E'
      },
      boxShadow: {
        neon: '0 0 12px #FF3D6B'
      }
    }
  },
  plugins: []
};

export default config;
