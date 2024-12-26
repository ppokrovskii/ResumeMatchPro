// File: src/app/App.tsx
// Test comment for commit hooks

import { MsalProvider } from '@azure/msal-react';
import React, { ReactNode } from 'react';
import { createBrowserRouter, createRoutesFromElements, Navigate, Outlet, Route, RouterProvider } from 'react-router-dom';
import './App.css';
import AuthenticationTemplate from './components/auth/AuthenticationTemplate';
import AuthCallback from './components/AuthCallback/AuthCallback';
import { MainLayout } from './components/layout/MainLayout';
import { msalInstance } from './contexts/AuthContext';
import HomePage from './pages/Homeage/HomePage';

const AuthenticatedRoute: React.FC<{ children: ReactNode }> = ({ children }) => (
  <AuthenticationTemplate>{children}</AuthenticationTemplate>
);

// Define the root layout that includes MainLayout and Outlet for nested routes
const RootLayout: React.FC = () => (
  <MainLayout>
    <Outlet />
  </MainLayout>
);

// Create the router configuration
const router = createBrowserRouter(
  createRoutesFromElements(
    <Route element={<RootLayout />}>
      <Route path="/auth-callback" element={<AuthCallback />} />
      <Route
        path="/"
        element={<AuthenticatedRoute><HomePage /></AuthenticatedRoute>}
      />
      <Route
        path="*"
        element={<AuthenticatedRoute><Navigate to="/" /></AuthenticatedRoute>}
      />
    </Route>
  )
);

const App: React.FC = () => {
  return (
    <MsalProvider instance={msalInstance}>
      <RouterProvider router={router} />
    </MsalProvider>
  );
};

export default App;
