import { render as rtlRender } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';

type RenderOptions = {
  route?: string;
  useRouterProvider?: boolean;
};

// Custom render function that includes Router
export function render(ui: React.ReactElement, { route = '/', useRouterProvider = false }: RenderOptions = {}) {
  window.history.pushState({}, 'Test page', route);

  if (useRouterProvider) {
    // Don't wrap with any router when useRouterProvider is true
    return rtlRender(ui);
  }

  // For components that don't need the full router setup
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

