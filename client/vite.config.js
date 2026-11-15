import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()], //Vite에게 "이 프로젝트는 React 프로젝트니까, React 전용 기능들을 적용해줘!"라고 설정(플러그인 등록)하는 부분
    server: {
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:3000',
                changeOrigin: true,
            },
        },
    },
});
