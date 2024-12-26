import React from 'react';
import { render, screen } from '@testing-library/react';
import { useMsal } from '@azure/msal-react';
import { AccountInfo } from '@azure/msal-browser';
import { AuthProvider, useAuth } from './AuthContext';

// Mock useMsal hook
jest.mock('@azure/msal-react', () => ({
  useMsal: jest.fn()
}));

const mockAccount: AccountInfo = {
  homeAccountId: 'test-account-id',
  localAccountId: 'test-local-id',
  environment: 'test-env',
  tenantId: 'test-tenant',
  username: 'test@example.com'
};

// Test component that uses the auth context
const TestComponent = () => {
  const { isAuthenticated, account } = useAuth();
  return (
    <div>
      <div>Is Authenticated: {isAuthenticated.toString()}</div>
      {account && <div>Username: {account.username}</div>}
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    (useMsal as jest.Mock).mockReturnValue({
      accounts: [mockAccount]
    });
  });

  it('provides authentication state', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText('Is Authenticated: true')).toBeInTheDocument();
    expect(screen.getByText('Username: test@example.com')).toBeInTheDocument();
  });

  it('handles no account state', () => {
    (useMsal as jest.Mock).mockReturnValue({
      accounts: []
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText('Is Authenticated: false')).toBeInTheDocument();
    expect(screen.queryByText(/Username:/)).not.toBeInTheDocument();
  });
}); 