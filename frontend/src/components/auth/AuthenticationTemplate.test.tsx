import { useMsal } from '@azure/msal-react';
import { render, screen, waitFor } from '@test-utils';
import AuthenticationTemplate from './AuthenticationTemplate';

// Mock useMsal hook
jest.mock('@azure/msal-react', () => ({
  useMsal: jest.fn(),
}));

describe('AuthenticationTemplate', () => {
  const mockOnAuthenticated = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('initiates login redirect when not authenticated', async () => {
    const mockLoginRedirect = jest.fn().mockResolvedValue(undefined);
    const mockHandleRedirectPromise = jest.fn().mockResolvedValue(null);

    (useMsal as jest.Mock).mockReturnValue({
      instance: {
        loginRedirect: mockLoginRedirect,
        handleRedirectPromise: mockHandleRedirectPromise,
      },
      accounts: [],
    });

    render(
      <AuthenticationTemplate onAuthenticated={mockOnAuthenticated}>
        <div>Protected Content</div>
      </AuthenticationTemplate>
    );

    // Wait for handleRedirectPromise to be called
    await waitFor(() => {
      expect(mockHandleRedirectPromise).toHaveBeenCalled();
    });

    // Wait for loginRedirect to be called since we're not authenticated
    await waitFor(() => {
      expect(mockLoginRedirect).toHaveBeenCalled();
    });

    // Content should not be rendered when not authenticated
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    expect(mockOnAuthenticated).not.toHaveBeenCalled();
  });

  it('handles successful redirect and shows content', async () => {
    const mockAccount = {
      name: 'Test User',
      homeAccountId: 'test-id',
      environment: 'test-env',
      tenantId: 'test-tenant',
      username: 'test@example.com',
    };

    const mockHandleRedirectPromise = jest.fn().mockResolvedValue({
      account: mockAccount,
    });

    (useMsal as jest.Mock).mockReturnValue({
      instance: {
        handleRedirectPromise: mockHandleRedirectPromise,
      },
      accounts: [mockAccount],
    });

    render(
      <AuthenticationTemplate onAuthenticated={mockOnAuthenticated}>
        <div>Protected Content</div>
      </AuthenticationTemplate>
    );

    // Wait for handleRedirectPromise to be called
    await waitFor(() => {
      expect(mockHandleRedirectPromise).toHaveBeenCalled();
    });

    // Wait for onAuthenticated to be called with the account from the redirect result
    await waitFor(() => {
      expect(mockOnAuthenticated).toHaveBeenCalledWith(mockAccount);
    });

    // Content should be rendered since we're authenticated
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('shows content when already authenticated', async () => {
    const mockAccount = {
      name: 'Test User',
      homeAccountId: 'test-id',
      environment: 'test-env',
      tenantId: 'test-tenant',
      username: 'test@example.com',
    };

    const mockHandleRedirectPromise = jest.fn().mockResolvedValue(null);

    (useMsal as jest.Mock).mockReturnValue({
      instance: {
        handleRedirectPromise: mockHandleRedirectPromise,
      },
      accounts: [mockAccount],
    });

    render(
      <AuthenticationTemplate onAuthenticated={mockOnAuthenticated}>
        <div>Protected Content</div>
      </AuthenticationTemplate>
    );

    // Wait for handleRedirectPromise to be called
    await waitFor(() => {
      expect(mockHandleRedirectPromise).toHaveBeenCalled();
    });

    // Wait for onAuthenticated to be called with the first account
    await waitFor(() => {
      expect(mockOnAuthenticated).toHaveBeenCalledWith(mockAccount);
    });

    // Content should be rendered since we're authenticated
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });
}); 