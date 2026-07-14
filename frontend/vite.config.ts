import { defineConfig } from 'vite';
import preact from '@preact/preset-vite';

export default defineConfig({
	plugins: [
		preact({
			prerender: {
				enabled: true,
				renderTarget: '#app',
				previewMiddlewareEnabled: true,
				additionalPrerenderRoutes: [
					'/login',
					'/signup',
					'/my/rooms',
					'/my/profile',
					'/room/create',
				],
			},
		}),
	],
	server: {
		proxy: {
			'/api/v1': {
				target: 'http://localhost:8000',
				changeOrigin: true,
			},
		},
	},
});