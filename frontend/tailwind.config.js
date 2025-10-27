/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        spotify: {
          green: '#1DB954',
          dark: '#191414',
          gray: '#282828',
          lightgray: '#b3b3b3',
        }
      }
    },
  },
  plugins: [],
}
