import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: 'localhost',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy) => {
          // Rewrite Set-Cookie so the session cookie applies to the dev server origin (localhost:5173)
          proxy.on('proxyRes', (proxyRes) => {
            const setCookie = proxyRes.headers['set-cookie'];
            if (setCookie) {
              proxyRes.headers['set-cookie'] = (Array.isArray(setCookie) ? setCookie : [setCookie]).map((c: string) =>
                c
                  .replace(/;\s*Domain=[^;]+/gi, '')
                  .replace(/;\s*Secure/gi, '')
                  .trim()
              );
            }
          });
        },
      },
    },
  },
  base: '/', // Ensure base path is root for static assets
  build: {
    assetsDir: 'assets',
    // Ensure public assets are copied correctly
    copyPublicDir: true,
  },
})
