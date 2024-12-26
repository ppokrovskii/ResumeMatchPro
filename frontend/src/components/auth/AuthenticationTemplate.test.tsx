import React from 'react';
import { render, screen } from '@testing-library/react';
import { useMsal } from '@azure/msal-react';
import { AccountInfo } from '@azure/msal-browser';
import AuthenticationTemplate from './AuthenticationTemplate';

// Mock useMsal hook
jest.mock('@azure/msal-react', () => ({
  useMsal: jest.fn()
}));

describe('AuthenticationTemplate', () => {
  const mockAccount: AccountInfo = {
    homeAccountId: 'test-account-id',
    localAccountId: 'test-local-id',
    environment: 'test-env',
    tenantId: 'test-tenant',
    username: 'test@example.com'
  };

  beforeEach(() => {
    (useMsal as jest.Mock).mockReturnValue({
      accounts: [mockAccount]
    });
  });

  it('renders children', () => {
    render(
      <AuthenticationTemplate>
        <div>Test Content</div>
      </AuthenticationTemplate>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('calls onAuthenticated when account is available', () => {
    const onAuthenticated = jest.fn();
    render(
      <AuthenticationTemplate onAuthenticated={onAuthenticated}>
        <div>Test Content</div>
      </AuthenticationTemplate>
    );

    expect(onAuthenticated).toHaveBeenCalledWith(mockAccount);
  });
}); 