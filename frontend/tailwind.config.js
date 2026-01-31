/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                cyber: {
                    blue: '#1e3a8a',
                    dark: '#0f172a',
                    darker: '#020617',
                    accent: '#06b6d4', // Cyan
                    green: '#10b981',
                    text: '#e2e8f0',
                }
            },
            fontFamily: {
                sans: ['Inter', 'Roboto', 'sans-serif'],
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
        },
    },
    plugins: [],
}
