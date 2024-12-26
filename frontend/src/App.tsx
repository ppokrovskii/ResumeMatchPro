// File: src/app/App.tsx

import { MsalProvider } from '@azure/msal-react';
import React from 'react';
import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import './App.css';
import AuthenticationTemplate from './components/auth/AuthenticationTemplate';
import AuthCallback from './components/AuthCallback/AuthCallback';
import { MainLayout } from './components/layout/MainLayout';
import { msalInstance } from './contexts/AuthContext';
import HomePage from './pages/Homeage/HomePage';

const MainContent = () => (
  <Routes>
    <Route path="/" element={<HomePage />} />
    <Route path="*" element={<Navigate to="/" />} />
  </Routes>
);

const App: React.FC = () => {
  return (
    <MsalProvider instance={msalInstance}>
      <Router>
        <MainLayout>
          <Routes>
            <Route path="/auth-callback" element={<AuthCallback />} />
            <Route
              path="/*"
              element={
                <AuthenticationTemplate>
                  <MainContent />
                </AuthenticationTemplate>
              }
            />
          </Routes>
        </MainLayout>
      </Router>
    </MsalProvider>
  );
};

export default App;
