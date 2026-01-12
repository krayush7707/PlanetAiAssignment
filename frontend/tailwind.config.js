/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: '#4CAF50',
                    hover: '#43A047',
                },
                secondary: {
                    DEFAULT: '#2196F3',
                    hover: '#1976D2',
                },
            },
        },
    },
    plugins: [],
}
