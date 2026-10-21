import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const { API_PORT = '3002' } = loadEnv(mode, process.cwd(), '')
  return {
    server: {
      proxy: {
        '/api': `http://127.0.0.1:${API_PORT}`,
      },
    },
  }
})
