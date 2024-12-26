import { useMsal } from '@azure/msal-react';
import { render, screen } from '@test-utils';
import AuthenticationTemplate from './AuthenticationTemplate';

// Mock useMsal hook
jest.mock('@azure/msal-react', () => ({
  useMsal: jest.fn(),
}));

describe('AuthenticationTemplate', () => {
  const mockAccount = {
    homeAccountId: 'test-account-id',
    environment: 'test-environment',
    tenantId: 'test-tenant-id',
    username: 'test@example.com',
  };

  beforeEach(() => {
    (useMsal as jest.Mock).mockReturnValue({
      accounts: [mockAccount],
      instance: {
        loginRedirect: jest.fn(),
      },
    });
  });

  it('renders children when authenticated', () => {
    render(
      <AuthenticationTemplate>
        <div>Test Content</div>
      </AuthenticationTemplate>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });
}); 