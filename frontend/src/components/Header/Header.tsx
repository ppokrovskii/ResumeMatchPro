// File: src/components/Header/Header.tsx

import { AccountInfo } from '@azure/msal-browser';
import { useMsal } from '@azure/msal-react';
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiTokenRequest, loginRequest } from '../../authConfig';
import './Header.css';

interface TokenInfo {
  loginScopes?: string[];
  apiScopes?: string[];
  error?: string;
}

const Header: React.FC = () => {
  const { instance, accounts } = useMsal();
  const [showDebug, setShowDebug] = useState(false);
  const [account, setAccount] = useState<AccountInfo | null>(null);
  const [tokenInfo, setTokenInfo] = useState<TokenInfo | null>(null);

  useEffect(() => {
    setAccount(accounts[0] ?? null);
  }, [accounts]);

  const getTokenInfo = async () => {
    if (!account) return;

    try {
      // Get login token info
      const loginTokenResult = await instance.acquireTokenSilent(loginRequest);

      // Try to get API token info
      let apiTokenResult = null;
      try {
        apiTokenResult = await instance.acquireTokenSilent(apiTokenRequest);
      } catch (error) {
        console.error('API token acquisition failed:', error);
      }

      setTokenInfo({
        loginScopes: loginTokenResult.scopes,
        apiScopes: apiTokenResult?.scopes,
      });
    } catch (error: unknown) {
      console.error('Error getting token info:', error);
      if (error instanceof Error) {
        setTokenInfo({ error: error.message });
      } else {
        setTokenInfo({ error: 'An unknown error occurred' });
      }
    }
  };

  const handleLogout = async () => {
    await instance.logoutRedirect();
  };

  const toggleDebug = () => {
    setShowDebug(!showDebug);
    if (!showDebug) {
      getTokenInfo();
    }
  };

  return (
    <header className="header">
      <nav>
        <Link to="/" className="logo">ResumeMatchPro</Link>
        <div className="nav-links">
          {account ? (
            <>
              <span className="user-info">
                {account.name || account.username}
              </span>
              <button onClick={toggleDebug} className="debug-button">
                {showDebug ? 'Hide Debug Info' : 'Show Debug Info'}
              </button>
              <button onClick={handleLogout} className="logout-button">
                Logout
              </button>
            </>
          ) : (
            <span>Not logged in</span>
          )}
        </div>
      </nav>

      {showDebug && account && (
        <div className="debug-info">
          <h3>Account Information</h3>
          <pre>{JSON.stringify(account, null, 2)}</pre>

          <h3>Token Information</h3>
          {tokenInfo ? (
            <div>
              <h4>Login Scopes</h4>
              <pre>{JSON.stringify(tokenInfo.loginScopes, null, 2)}</pre>

              <h4>API Scopes</h4>
              <pre>{JSON.stringify(tokenInfo.apiScopes, null, 2)}</pre>

              {tokenInfo.error && (
                <div className="error-message">
                  <h4>Error</h4>
                  <pre>{tokenInfo.error}</pre>
                </div>
              )}
            </div>
          ) : (
            <p>Loading token information...</p>
          )}
        </div>
      )}
    </header>
  );
};

export default Header;
