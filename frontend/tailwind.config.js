/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // VS Code dark theme colors
        'vscode': {
          'bg': '#1e1e1e',
          'sidebar': '#252526',
          'panel': '#1e1e1e',
          'border': '#3c3c3c',
          'text': '#cccccc',
          'text-dim': '#858585',
          'accent': '#007acc',
          'accent-hover': '#1177bb',
          'success': '#4ec9b0',
          'error': '#f14c4c',
          'warning': '#cca700',
          'selection': '#264f78',
        },
      },
      fontFamily: {
        'mono': ['Consolas', 'Monaco', 'Courier New', 'monospace'],
      },
    },
  },
  plugins: [],
}
