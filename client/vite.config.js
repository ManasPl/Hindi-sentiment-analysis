import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Base is set for GitHub Pages project-page deployment:
// https://manaspl.github.io/Hindi-sentiment-analysis/
// If you deploy elsewhere (Vercel/Netlify, or a custom domain), change this
// to '/' — otherwise asset paths (JS/CSS/model files) will 404.
export default defineConfig({
  base: '/Hindi-sentiment-analysis/',
  plugins: [react()],
})
