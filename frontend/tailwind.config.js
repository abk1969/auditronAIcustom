module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#4f83cc',
          main: '#1976d2',
          dark: '#115293',
        },
        secondary: {
          light: '#5c6bc0',
          main: '#3f51b5',
          dark: '#2c387e',
        },
        success: {
          light: '#81c784',
          main: '#4caf50',
          dark: '#388e3c',
        },
        warning: {
          light: '#ffb74d',
          main: '#ff9800',
          dark: '#f57c00',
        },
        error: {
          light: '#e57373',
          main: '#f44336',
          dark: '#d32f2f',
        },
      },
      fontFamily: {
        sans: ['Roboto', 'sans-serif'],
      },
      spacing: {
        '72': '18rem',
        '84': '21rem',
        '96': '24rem',
      },
      boxShadow: {
        card: '0 2px 4px rgba(0,0,0,0.1)',
        elevated: '0 4px 6px rgba(0,0,0,0.1)',
      },
    },
  },
  plugins: [],
  important: true,
}; 