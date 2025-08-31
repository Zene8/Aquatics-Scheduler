import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class', // Enable dark mode based on 'class'
  theme: {
    extend: {
      colors: {
        // Light mode colors
        primary: {
          DEFAULT: '#4A90E2', // A shade of blue
          light: '#7AAFF7',
          dark: '#2A6DBA',
        },
        accent: {
          DEFAULT: '#50E3C2', // A shade of teal/mint
          light: '#80F0D0',
          dark: '#2CA08A',
        },
        neutral: {
          DEFAULT: '#F5F5F5', // Light gray
          light: '#FFFFFF',
          dark: '#E0E0E0',
        },
        background: {
          DEFAULT: '#FFFFFF', // White
          light: '#F8F8F8',
          dark: '#F0F0F0',
        },
        // Dark mode colors (prefixed with 'dark-')
        'dark-primary': {
          DEFAULT: '#8E44AD', // A shade of purple
          light: '#B06ECF',
          dark: '#6D2F8C',
        },
        'dark-accent': {
          DEFAULT: '#F39C12', // A shade of orange
          light: '#FFB74D',
          dark: '#D68910',
        },
        'dark-neutral': {
          DEFAULT: '#333333', // Dark gray
          light: '#4F4F4F',
          dark: '#1A1A1A',
        },
        'dark-background': {
          DEFAULT: '#121212', // Darkest gray
          light: '#212121',
          dark: '#000000',
        },
      },
    },
  },
  plugins: [],
};

export default config;
