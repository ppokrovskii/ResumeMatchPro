// File: src/components/Header/Header.tsx

import React, { useState, useRef, useEffect } from 'react';
import { useMsal } from '@azure/msal-react';
import styles from './Header.module.css';

const Header: React.FC = () => {
  const { instance, accounts } = useMsal();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [showDebug, setShowDebug] = useState(false);
  const debugPanelRef = useRef<HTMLDivElement>(null);

  const claims = accounts[0]?.idTokenClaims;
  const isAdmin = claims?.['extension_IsAdmin'] === true;

  // Add debug logging
  console.log('User Claims:', claims);
  console.log('Is Admin:', isAdmin);

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

  // Only show debug in development
  const isDevelopment = process.env.NODE_ENV === 'development';

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
        {accounts.length > 0 && (
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
                {isDevelopment && (
                  <button 
                    onClick={toggleDebug}
                    className={styles.dropdownItem}
                  >
                    Toggle Debug Info
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
        )}
      </nav>
      {isDevelopment && showDebug && claims && (
        <div ref={debugPanelRef} className={styles.debugInfo}>
          <h3>Debug Information</h3>
          <h4>Environment Variables</h4>
          <pre>
            {JSON.stringify({
              REACT_APP_BASE_URL: process.env.REACT_APP_BASE_URL || 'not set',
              REACT_APP_API_URL: process.env.REACT_APP_API_URL || 'not set',
              REACT_APP_B2C_TENANT: process.env.REACT_APP_B2C_TENANT || 'not set',
              REACT_APP_B2C_CLIENT_ID: process.env.REACT_APP_B2C_CLIENT_ID || 'not set',
              REACT_APP_B2C_AUTHORITY_DOMAIN: process.env.REACT_APP_B2C_AUTHORITY_DOMAIN || 'not set'
            }, null, 2)}
          </pre>
          <h4>User Claims</h4>
          <pre>
            {JSON.stringify(claims, null, 2)}
          </pre>
        </div>
      )}
    </header>
  );
};

export default Header;
