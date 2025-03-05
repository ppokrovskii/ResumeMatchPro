// File: src/app/App.tsx
// Test comment for commit hooks

import { IPublicClientApplication } from '@azure/msal-browser';
import { MsalProvider } from '@azure/msal-react';
import { message } from 'antd';
import React, { useContext } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import styles from './App.module.css';
import AppRoutes from './AppRoutes';
import Footer from './components/Footer/Footer';
import GlobalDragDrop from './components/GlobalDragDrop';
import TopNavbar from './components/Nav/TopNavbar/TopNavbar';
import { AuthContext, AuthProvider } from './contexts/AuthContext';

interface AppProps {
  pca: IPublicClientApplication;
}

// Inner component to use context
const AppContent: React.FC = () => {
  const { isAuthenticated } = useContext(AuthContext);

  const handleFilesUploaded = (response: { files: { name: string }[] }) => {
    message.success(`${response.files.length} files uploaded successfully`);
    // Navigate to home page if not already there
    if (window.location.pathname !== '/') {
      window.location.href = '/';
    }
  };

  return (
    <div className={styles.app}>
      <TopNavbar />
      <main className={styles.mainContent}>
        <div className={styles.container}>
          {isAuthenticated ? (
            <GlobalDragDrop onFilesUploaded={handleFilesUploaded}>
              <AppRoutes />
            </GlobalDragDrop>
          ) : (
            <AppRoutes />
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
};

const App: React.FC<AppProps> = ({ pca }) => {
  return (
    <Router>
      <MsalProvider instance={pca}>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </MsalProvider>
    </Router>
  );
};

export default App;
