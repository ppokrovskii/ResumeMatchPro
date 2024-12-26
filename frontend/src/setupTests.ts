// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock window.crypto
const cryptoMock = {
  subtle: {
    digest: jest.fn(),
    encrypt: jest.fn(),
    decrypt: jest.fn(),
  },
  getRandomValues: jest.fn(),
};

Object.defineProperty(window, 'crypto', {
  value: cryptoMock,
});

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// suppress act() warnings
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (/Warning.*not wrapped in act/.test(args[0])) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});

// Configure Jest to handle async operations
jest.setTimeout(10000);

// Add global fetch mock
global.fetch = jest.fn(() => 
  Promise.resolve({
    json: () => Promise.resolve({}),
    ok: true,
  })
) as jest.Mock;

// Clear all mocks after each test
afterEach(() => {
  jest.clearAllMocks();
});
