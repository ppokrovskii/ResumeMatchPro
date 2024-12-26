import { render as rtlRender } from '@testing-library/react';
import React from 'react';
import { BrowserRouter, RouterProvider, createBrowserRouter } from 'react-router-dom';

type RenderOptions = {
  route?: string;
  useRouterProvider?: boolean;
};

// Custom render function that includes Router
export function render(ui: React.ReactElement, { route = '/', useRouterProvider = false }: RenderOptions = {}) {
  window.history.pushState({}, 'Test page', route);

  if (useRouterProvider) {
    const router = createBrowserRouter([
      {
        path: '*',
        element: ui,
      },
    ], {
      future: {
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }
    });

    return rtlRender(<RouterProvider router={router} />);
  }

  return rtlRender(ui, {
    wrapper: ({ children }: { children: React.ReactNode }) => (
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        {children}
      </BrowserRouter>
    ),
  });
}

// re-export everything
export * from '@testing-library/react';

