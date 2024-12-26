import React from 'react';
import { render, screen } from '@testing-library/react';
import { AuthenticationTemplate } from './AuthenticationTemplate';
import { BrowserRouter } from 'react-router-dom';

// Mock MSAL components
const mockMsal = {
  errorMode: false,
  loadingMode: false,
  reset() {
    this.errorMode = false;
    this.loadingMode = false;
  }
};

jest.mock('@azure/msal-react', () => ({
  MsalAuthenticationTemplate: ({ children, errorComponent: ErrorComponent, loadingComponent: LoadingComponent }: any) => {
    if (mockMsal.errorMode) {
      return ErrorComponent({ error: { errorMessage: 'Test error' } });
    }
    if (mockMsal.loadingMode) {
      return LoadingComponent();
    }
    return children;
  },
  InteractionType: { Redirect: 'redirect' }
}));

describe('AuthenticationTemplate', () => {
  beforeEach(() => {
    mockMsal.reset();
  });

  it('renders children', () => {
    render(
      <BrowserRouter>
        <AuthenticationTemplate>
          <div>Test Content</div>
        </AuthenticationTemplate>
      </BrowserRouter>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('renders error message when authentication fails', () => {
    mockMsal.errorMode = true;

    render(
      <BrowserRouter>
        <AuthenticationTemplate>
          <div>Test Content</div>
        </AuthenticationTemplate>
      </BrowserRouter>
    );

    expect(screen.getByText('Authentication failed. Please try again.')).toBeInTheDocument();
  });

  it('renders loading message during authentication', () => {
    mockMsal.loadingMode = true;

    render(
      <BrowserRouter>
        <AuthenticationTemplate>
          <div>Test Content</div>
        </AuthenticationTemplate>
      </BrowserRouter>
    );

    expect(screen.getByText('Processing authentication...')).toBeInTheDocument();
  });
}); 