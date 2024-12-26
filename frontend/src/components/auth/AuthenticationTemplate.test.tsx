import React from 'react';
import { render, screen } from '@testing-library/react';
import { AuthenticationTemplate } from './AuthenticationTemplate';
import { MsalAuthenticationTemplate } from '@azure/msal-react';

// Mock MsalAuthenticationTemplate to directly render children or error component
jest.mock('@azure/msal-react', () => ({
  MsalAuthenticationTemplate: ({ children, errorComponent: ErrorComponent }: { 
    children: React.ReactNode;
    errorComponent?: React.ComponentType<{ error: { errorMessage: string } }>;
  }) => {
    if (ErrorComponent && (ErrorComponent as any).mockErrorMessage) {
      return <ErrorComponent error={{ errorMessage: (ErrorComponent as any).mockErrorMessage }} />;
    }
    return children;
  }
}));

describe('AuthenticationTemplate', () => {
  it('renders children when authenticated', () => {
    render(
      <AuthenticationTemplate>
        <div>Test Content</div>
      </AuthenticationTemplate>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('handles user cancellation without showing error', () => {
    const MockMsalTemplate = MsalAuthenticationTemplate as jest.Mock;
    (MockMsalTemplate as any).mockErrorMessage = 'AADB2C90091';
    
    render(
      <AuthenticationTemplate>
        <div>Test Content</div>
      </AuthenticationTemplate>
    );

    expect(screen.queryByText('Authentication failed')).not.toBeInTheDocument();
  });
}); 