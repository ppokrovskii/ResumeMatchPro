import { useMsal } from '@azure/msal-react';
import { fireEvent, render, screen } from '@test-utils';
import Header from '../Header';

// Mock useMsal hook
jest.mock('@azure/msal-react', () => ({
  useMsal: jest.fn(),
}));

describe('Header', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    jest.resetModules();
    process.env = { ...originalEnv, NODE_ENV: 'development' };
  });

  afterEach(() => {
    process.env = originalEnv;
    jest.clearAllMocks();
  });

  it('shows user menu with user name', () => {
    const mockAccount = {
      name: 'Test User',
      homeAccountId: 'test-id',
      environment: 'test-env',
      tenantId: 'test-tenant',
      username: 'test@example.com',
    };

    (useMsal as jest.Mock).mockReturnValue({
      instance: {
        getConfiguration: () => ({
          auth: {
            authority: 'test-authority',
            redirectUri: 'test-redirect-uri',
          }
        }),
        getActiveAccount: () => mockAccount,
        logoutRedirect: jest.fn(),
      },
      accounts: [mockAccount],
    });

    render(<Header />);
    
    expect(screen.getByText('Debug Info')).toBeInTheDocument();
    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.queryByText('Debug Information')).not.toBeInTheDocument();

    // Click Debug Info button
    fireEvent.click(screen.getByText('Debug Info'));
    expect(screen.getByText('Debug Information')).toBeInTheDocument();
  });

  it('shows admin indicator for admin users', () => {
    const mockAccount = {
      name: 'Test User',
      homeAccountId: 'test-id',
      environment: 'test-env',
      tenantId: 'test-tenant',
      username: 'test@example.com',
      idTokenClaims: {
        extension_IsAdmin: true,
      },
    };

    (useMsal as jest.Mock).mockReturnValue({
      instance: {
        getConfiguration: () => ({
          auth: {
            authority: 'test-authority',
            redirectUri: 'test-redirect-uri',
          }
        }),
        getActiveAccount: () => mockAccount,
        logoutRedirect: jest.fn(),
      },
      accounts: [mockAccount],
    });

    render(<Header />);
    
    expect(screen.getByText('Test User (Admin)')).toBeInTheDocument();
    expect(screen.getByText('Debug Info')).toBeInTheDocument();

    // Open user menu
    fireEvent.click(screen.getByText('Test User (Admin)'));
    expect(screen.getByText('Admin Panel')).toBeInTheDocument();
  });

  it('shows debug panel with environment information', () => {
    const mockAccount = {
      name: 'Test User',
      homeAccountId: 'test-id',
      environment: 'test-env',
      tenantId: 'test-tenant',
      username: 'test@example.com',
    };

    (useMsal as jest.Mock).mockReturnValue({
      instance: {
        getConfiguration: () => ({
          auth: {
            authority: 'test-authority',
            redirectUri: 'test-redirect-uri',
          }
        }),
        getActiveAccount: () => mockAccount,
        logoutRedirect: jest.fn(),
      },
      accounts: [mockAccount],
    });

    render(<Header />);

    // Click Debug Info button
    fireEvent.click(screen.getByText('Debug Info'));
    
    expect(screen.getByText('Debug Information')).toBeInTheDocument();
    expect(screen.getByText('Authentication State')).toBeInTheDocument();
    expect(screen.getByText('Environment Variables')).toBeInTheDocument();
    expect(screen.getByText('MSAL Configuration')).toBeInTheDocument();
  });
}); 