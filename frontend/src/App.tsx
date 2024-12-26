// File: src/app/App.tsx

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { MsalProvider } from '@azure/msal-react';
import { msalInstance } from './contexts/AuthContext';
import { AuthenticationTemplate } from './components/auth/AuthenticationTemplate';
import { MainLayout } from './components/layout/MainLayout';
import HomePage from './pages/Homeage/HomePage';
import AuthCallback from './components/AuthCallback/AuthCallback';
import './App.css';

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
