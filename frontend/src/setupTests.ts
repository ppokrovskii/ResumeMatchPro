// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock window.crypto
Object.defineProperty(window, 'crypto', {
  value: {
    getRandomValues: (arr: Uint8Array) => crypto.getRandomValues(arr),
  },
});

// Suppress specific console errors during tests
const originalError = console.error;
console.error = (...args: unknown[]) => {
  if (typeof args[0] === 'string') {
    if (args[0].includes('Warning: ReactDOM.render is no longer supported')) {
      return;
    }
    if (args[0].includes('Warning: `ReactDOMTestUtils.act` is deprecated')) {
      return;
    }
  }
  originalError.call(console, ...args);
};

// Configure Jest to handle async operations
jest.setTimeout(10000);
