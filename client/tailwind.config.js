/** @type {import('tailwindcss').Config} */
import { nextui } from "@nextui-org/react";

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./node_modules/@nextui-org/theme/dist/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    fontFamily: {
      'sans': ['Poppins', 'sans-serif'],
      'display': ['Poppins', 'sans-serif'],
      'body': ['Poppins', 'sans-serif'],
    },
    extend: {
      fontSize : {
        'display': '2rem',
        'title.large': '1.625rem',
        'title.base': '1.5rem',
        'subtitle': '1.25rem',
        'body.large': '1.125rem',
        'body.strong': '1.0625rem',
        'body.base': '1.0625rem',
        'caption': '1rem',
      },
      fontWeight: {
        'display': '700',
        'title': '700',
        'subtitle': '600',
        'body': '400',
        'caption': '400',
      },
    },
  },
  darkMode: "class",
  plugins: [
    nextui({
      themes: {
        light: {
          colors: {
            primary : {
              base: '#4F75FE',
              hover: '#4161D5'
            },
            secondary : {
              base: '#FFBB00',
              hover: '#C79200'
            },
            tertiary : {
              base: '#F03842',
              hover: '#C62A33'
            },
            surface: '#EEE9DF',
            background: '#FBF9F5',
            text: '#181818',
            white: '#FFFFFF',
          }
        }
      }
    })
  ],
}

