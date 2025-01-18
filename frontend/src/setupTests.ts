// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock environment variables
process.env.REACT_APP_BASE_URL = 'http://localhost:3000';

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

// Mock window.matchMedia for Ant Design components
window.matchMedia = window.matchMedia || function () {
  return {
    matches: false,
    addListener: function () { },
    removeListener: function () { },
    addEventListener: function () { },
    removeEventListener: function () { },
    dispatchEvent: function () { return true; },
    onchange: null,
    media: '',
  };
};

// Mock MSAL LogLevel
jest.mock('@azure/msal-browser', () => ({
  LogLevel: {
    Error: 0,
    Warning: 1,
    Info: 2,
    Verbose: 3,
  }
}));

// Configure Jest to handle async operations
jest.setTimeout(10000);
