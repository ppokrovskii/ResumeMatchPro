// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{html,js,tsx}"],
  theme: {
    extend: {
      colors: {
        // Define default and dark theme colors as variables
        'bg': 'var(--color-bg)',
        'bg-primary': 'var(--color-bg-primary)',
        'bg-contrast': 'var(--color-bg-contrast)',
        'bg-secondary': 'var(--color-bg-secondary)',
        'text-primary': 'var(--color-text-primary)',
        'text-secondary': 'var(--color-text-secondary)',
        'text-regular': 'var(--color-text-regular)',
        'button-primary': 'var(--color-button-primary)',
        'button-secondary': 'var(--color-button-secondary)',
        'button-regular': 'var(--color-button-regular)',
      },
      fontFamily: {
        sans: ['Roboto', 'sans-serif'],
        mono: ['var(--font-roboto-mono)'],
        worksans: ['Work Sans', 'sans-serif'],
        montserratAlt: ['MontserratAlt1', 'sans-serif'],
      },
    },
  },
  plugins: [
    function({ addUtilities }) {
      const newUtilities = {
        '.gradient-text': {
          background: 'linear-gradient(90deg, var(--gradient-start), var(--gradient-end))',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
        },
        '.font-thin': {
          fontWeight: '300', // Light weight
        },
      }
      addUtilities(newUtilities, ['responsive', 'hover'])
    }
  ],
}
