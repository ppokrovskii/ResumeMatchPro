// File: src/app/App.tsx
// Test comment for commit hooks

import { IPublicClientApplication } from '@azure/msal-browser';
import { MsalProvider } from '@azure/msal-react';
import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import styles from './App.module.css';
import AppRoutes from './AppRoutes';
import Footer from './components/Footer/Footer';
import TopNavbar from './components/Nav/TopNavbar/TopNavbar';
import { AuthProvider } from './contexts/AuthContext';

interface AppProps {
  pca: IPublicClientApplication;
}

const App: React.FC<AppProps> = ({ pca }) => {
  return (
    <Router>
      <MsalProvider instance={pca}>
        <AuthProvider>
          <div className={styles.app}>
            <TopNavbar />
            <main className={styles.mainContent}>
              <div className={styles.container}>
                <AppRoutes />
              </div>
            </main>
            <Footer />
          </div>
        </AuthProvider>
      </MsalProvider>
    </Router>
  );
};

export default App;
