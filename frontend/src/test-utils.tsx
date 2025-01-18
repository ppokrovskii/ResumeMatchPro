import { render as rtlRender } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';

type RenderOptions = {
  route?: string;
  useRouterProvider?: boolean;
};

// Simple mock for MSAL that bypasses authentication
jest.mock('@azure/msal-react', () => ({
  useMsal: () => ({
    instance: {
      getActiveAccount: () => ({
        idTokenClaims: { oid: 'test-user-id' }
      }),
      getAllAccounts: () => [{
        idTokenClaims: { oid: 'test-user-id' }
      }]
    },
    accounts: [{
      idTokenClaims: { oid: 'test-user-id' }
    }],
    inProgress: 'none'
  }),
  MsalProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));

// Custom render function that includes Router
export function render(ui: React.ReactElement, { route = '/', useRouterProvider = false }: RenderOptions = {}) {
  window.history.pushState({}, 'Test page', route);

  if (useRouterProvider) {
    return rtlRender(ui);
  }

  return rtlRender(ui, {
    wrapper: ({ children }: { children: React.ReactNode }) => (
      <MemoryRouter initialEntries={[route]}>
        {children}
      </MemoryRouter>
    ),
  });
}

// re-export everything
export * from '@testing-library/react';

