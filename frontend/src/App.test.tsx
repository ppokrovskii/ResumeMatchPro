import React from 'react';
import { render } from '@testing-library/react';
import App from './App';

// Mock all required modules
jest.mock('./contexts/AuthContext', () => ({
  msalInstance: {
    initialize: jest.fn().mockResolvedValue(undefined),
    handleRedirectPromise: jest.fn().mockResolvedValue(null),
  }
}));

jest.mock('./components/auth/AuthenticationTemplate', () => ({
  AuthenticationTemplate: ({ children }: { children: React.ReactNode }) => <div>{children}</div>
}));

jest.mock('./components/layout/MainLayout', () => ({
  MainLayout: ({ children }: { children: React.ReactNode }) => <div>{children}</div>
}));

jest.mock('@azure/msal-react', () => ({
  MsalProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>
}));

jest.mock('./pages/Homeage/HomePage', () => ({
  __esModule: true,
  default: () => <div>Home Page Content</div>
}));

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />);
  });
});

