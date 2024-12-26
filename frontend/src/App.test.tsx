import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
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

describe('App Component', () => {
  it('renders without crashing', async () => {
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('Home Page Content')).toBeInTheDocument();
    });
  });
});

