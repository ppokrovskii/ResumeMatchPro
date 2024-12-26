import { useMsal } from '@azure/msal-react';
import { render, screen } from '@test-utils';
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

  it('shows Debug Info link in development mode when not authenticated', () => {
    // Mock unauthenticated state
    (useMsal as jest.Mock).mockReturnValue({
      instance: {
        getConfiguration: () => ({
          auth: {
            authority: 'test-authority',
            redirectUri: 'test-redirect-uri',
          }
        }),
        getActiveAccount: () => null,
        logoutRedirect: jest.fn(),
      },
      accounts: [],
    });

    render(<Header />);
    
    expect(screen.getByText('Debug Info')).toBeInTheDocument();
    expect(screen.getByText('Sign In')).toBeInTheDocument();
  });

  it('shows Debug Info link in development mode when authenticated', () => {
    // Mock authenticated state
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
  });

  it('hides Debug Info link in production mode', () => {
    // Set NODE_ENV to production for this test
    process.env = { ...originalEnv, NODE_ENV: 'production' };

    (useMsal as jest.Mock).mockReturnValue({
      instance: {
        getConfiguration: () => ({
          auth: {
            authority: 'test-authority',
            redirectUri: 'test-redirect-uri',
          }
        }),
        getActiveAccount: () => null,
        logoutRedirect: jest.fn(),
      },
      accounts: [],
    });

    render(<Header />);
    
    expect(screen.queryByText('Debug Info')).not.toBeInTheDocument();
  });
}); 