import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({plugins:[react()],build:{outDir:'../backend/static/js/react',emptyOutDir:true,rollupOptions:{input:'src/main.jsx',output:{entryFileNames:'app.js',chunkFileNames:'app.js',assetFileNames:'[name][extname]',inlineDynamicImports:true}}}});
