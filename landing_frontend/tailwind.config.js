// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{html,js,tsx}"],
  theme: {
    extend: {
      colors: {
        // regular
        'text': 'var(--color-text)',
        'bg': 'var(--color-bg)',
        'button-text': 'var(--color-button-text)',
        'button-bg': 'var(--color-button-bg)',
        // primary
        'text-primary': 'var(--color-text-primary)',
        'bg-primary': 'var(--color-bg-primary)',
        'button-text-primary': 'var(--color-button-text-primary)',
        'button-bg-primary': 'var(--color-button-bg-primary)',
        // secondary
        'text-secondary': 'var(--color-text-secondary)',
        'bg-secondary': 'var(--color-bg-secondary)',
        'button-text-secondary': 'var(--color-button-text-secondary)',
        'button-bg-secondary': 'var(--color-button-bg-secondary)',
        // accent
        'text-accent': 'var(--color-text-accent)',
        'bg-accent': 'var(--color-bg-accent)',
        'button-text-accent': 'var(--color-button-text-accent)',
        'button-bg-accent': 'var(--color-button-bg-accent)',
      },
      fontFamily: {
        sans: ['Roboto', 'sans-serif'],
        mono: ['var(--font-roboto-mono)'],
        worksans: ['Work Sans', 'sans-serif'],
        montserratAlt: ['MontserratAlt1', 'sans-serif'],
      },
      spacing: {
        '1': '4px',
      }
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
