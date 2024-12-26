// File: src/app/App.tsx
// Test comment for commit hooks

import { MsalProvider } from '@azure/msal-react';
import React from 'react';
import { Navigate, Route, RouterProvider, Routes, createBrowserRouter, createRoutesFromElements } from 'react-router-dom';
import './App.css';
import AuthenticationTemplate from './components/auth/AuthenticationTemplate';
import AuthCallback from './components/AuthCallback/AuthCallback';
import { MainLayout } from './components/layout/MainLayout';
import { msalInstance } from './contexts/AuthContext';
import HomePage from './pages/Homeage/HomePage';

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route element={<MainLayout />}>
      <Route path="/auth-callback" element={<AuthCallback />} />
      <Route
        path="/*"
        element={
          <AuthenticationTemplate>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </AuthenticationTemplate>
        }
      />
    </Route>
  ),
  {
    future: {
      v7_startTransition: true,
      v7_relativeSplatPath: true
    }
  }
);

const App: React.FC = () => {
  return (
    <MsalProvider instance={msalInstance}>
      <RouterProvider router={router} />
    </MsalProvider>
  );
};

export default App;
