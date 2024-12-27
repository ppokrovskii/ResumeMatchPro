const path = require('path');

module.exports = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@test-utils': path.resolve(__dirname, 'src/test-utils'),
    },
  },
  jest: {
    configure: {
      moduleNameMapper: {
        '^@/(.*)$': '<rootDir>/src/$1',
        '^@test-utils$': '<rootDir>/src/test-utils',
      },
    },
  },
}; 