/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        '../../**/templates/**/*.html',
        '../../**/templates/*.html',
    ],
    theme: {
        extend: {
            colors: {
                'primary': '#1a202c',
                'secondary': '#2d3748',
                'accent': '#4a5568',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
} 