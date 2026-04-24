import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current directory and its parent directories
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    base: './',
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
        '/Goros/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/Goros/, ''),
        },
      },
    },
    // Pass environment variables to the client
    define: {
      __APP_ENV__: JSON.stringify(env.APP_ENV || 'development'),
      __ALLOW_MANUAL_SYNC__: JSON.stringify(env.ALLOW_MANUAL_SYNC !== 'false'),
    },
  }
})
