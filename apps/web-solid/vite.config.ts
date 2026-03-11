import { defineConfig } from 'vite'
import solid from 'vite-plugin-solid'
import tailwindcss from '@tailwindcss/vite'
import { visualizer } from 'rollup-plugin-visualizer'
import { fileURLToPath } from 'url'
import path from 'path'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [
    solid(),
    tailwindcss(),
    visualizer({ filename: 'docs/bundle-report.html', open: false, gzipSize: true }),
  ],
  resolve: { alias: { '@': path.resolve(__dirname, './src') } },
  server: { port: 3001 }
})
