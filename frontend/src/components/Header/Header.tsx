// File: src/components/Header/Header.tsx

import React, { useState, useRef, useEffect } from 'react';
import { useMsal } from '@azure/msal-react';
import styles from './Header.module.css';

const Header: React.FC = () => {
  const { instance, accounts } = useMsal();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [showDebug, setShowDebug] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const debugPanelRef = useRef<HTMLDivElement>(null);
  const isDevelopment = process.env.NODE_ENV === 'development';

  const claims = accounts[0]?.idTokenClaims;
  const isAdmin = claims?.['extension_IsAdmin'] === true;

  // Log authentication state on mount and when accounts change
  useEffect(() => {
    if (isDevelopment) {
      const msalInfo = {
        config: instance.getConfiguration(),
        activeAccount: instance.getActiveAccount(),
        accounts: accounts,
        authority: instance.getConfiguration().auth.authority,
        redirectUri: instance.getConfiguration().auth.redirectUri,
      };
      
      const envInfo = {
        NODE_ENV: process.env.NODE_ENV,
        BASE_URL: process.env.REACT_APP_BASE_URL,
        API_URL: process.env.REACT_APP_API_URL,
        B2C_TENANT: process.env.REACT_APP_B2C_TENANT,
        B2C_AUTHORITY_DOMAIN: process.env.REACT_APP_B2C_AUTHORITY_DOMAIN,
      };

      console.log('Auth State:', {
        isAuthenticated: accounts.length > 0,
        accountsCount: accounts.length,
        accounts: accounts,
      });
      console.log('MSAL Instance:', msalInfo);
      console.log('Environment:', envInfo);

      if (claims) {
        console.log('User Claims:', claims);
        console.log('Is Admin:', isAdmin);
      }
    }
  }, [accounts, claims, isAdmin, instance]);

  const handleLogin = async () => {
    if (isLoggingIn) {
      console.log('Login already in progress...');
      return;
    }

    try {
      setIsLoggingIn(true);
      console.log('Attempting login...');
      
      // Check if there's an interaction in progress
      if (instance.getActiveAccount() === null) {
        try {
          await instance.handleRedirectPromise();
        } catch (e) {
          console.log('No redirect promise to handle');
        }
      }

      await instance.loginRedirect();
      console.log('Login redirect initiated');
    } catch (error: any) {
      console.error('Login error:', error);
      if (error.errorCode === 'interaction_in_progress') {
        console.log('Attempting to handle existing interaction...');
        try {
          await instance.handleRedirectPromise();
          if (!accounts.length) {
            // If still not authenticated after handling redirect, try login again
            await instance.loginRedirect();
          }
        } catch (redirectError) {
          console.error('Error handling redirect:', redirectError);
        }
      }
    } finally {
      setIsLoggingIn(false);
    }
  };

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (debugPanelRef.current && !debugPanelRef.current.contains(event.target as Node)) {
        setShowDebug(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLogout = async () => {
    try {
      await instance.logoutRedirect({
        postLogoutRedirectUri: window.location.origin,
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const toggleDebug = () => {
    setShowDebug(!showDebug);
  };

  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        ResumeMatchPro
      </div>
      <nav className={styles.nav}>
        {isDevelopment && (
          <button 
            onClick={toggleDebug}
            className={`${styles.userButton} ${styles.debugButton}`}
          >
            Debug Info
          </button>
        )}
        {accounts.length > 0 ? (
          <div className={styles.userMenu}>
            <button 
              onClick={toggleDropdown}
              className={styles.userButton}
            >
              {accounts[0].name || 'User'}{isAdmin ? ' (Admin)' : ''}
            </button>
            {isDropdownOpen && (
              <div className={styles.dropdown}>
                {isAdmin && (
                  <button 
                    onClick={() => {/* Navigate to admin panel */}}
                    className={styles.dropdownItem}
                  >
                    Admin Panel
                  </button>
                )}
                <button 
                  onClick={handleLogout}
                  className={styles.dropdownItem}
                >
                  Log Out
                </button>
              </div>
            )}
          </div>
        ) : (
          <button 
            onClick={handleLogin}
            className={styles.userButton}
            disabled={isLoggingIn}
          >
            {isLoggingIn ? 'Signing in...' : 'Sign In'}
          </button>
        )}
      </nav>
      {isDevelopment && showDebug && (
        <div ref={debugPanelRef} className={styles.debugInfo}>
          <h3>Debug Information</h3>
          <h4>Authentication State</h4>
          <pre>
            {JSON.stringify({
              isAuthenticated: accounts.length > 0,
              accountsCount: accounts.length,
              activeAccount: instance.getActiveAccount(),
            }, null, 2)}
          </pre>
          <h4>Environment Variables</h4>
          <pre>
            {JSON.stringify({
              NODE_ENV: process.env.NODE_ENV,
              REACT_APP_BASE_URL: process.env.REACT_APP_BASE_URL || 'not set',
              REACT_APP_API_URL: process.env.REACT_APP_API_URL || 'not set',
              REACT_APP_B2C_TENANT: process.env.REACT_APP_B2C_TENANT || 'not set',
              REACT_APP_B2C_CLIENT_ID: process.env.REACT_APP_B2C_CLIENT_ID || 'not set',
              REACT_APP_B2C_AUTHORITY_DOMAIN: process.env.REACT_APP_B2C_AUTHORITY_DOMAIN || 'not set'
            }, null, 2)}
          </pre>
          <h4>MSAL Configuration</h4>
          <pre>
            {JSON.stringify({
              authority: instance.getConfiguration().auth.authority,
              redirectUri: instance.getConfiguration().auth.redirectUri,
              postLogoutRedirectUri: instance.getConfiguration().auth.postLogoutRedirectUri,
              knownAuthorities: instance.getConfiguration().auth.knownAuthorities,
            }, null, 2)}
          </pre>
          {claims && (
            <>
              <h4>User Claims</h4>
              <pre>
                {JSON.stringify(claims, null, 2)}
              </pre>
            </>
          )}
        </div>
      )}
    </header>
  );
};

export default Header;
