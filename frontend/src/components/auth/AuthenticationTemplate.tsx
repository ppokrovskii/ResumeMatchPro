/* eslint-disable no-console */
import { AccountInfo, BrowserAuthError } from '@azure/msal-browser';
import { useMsal } from '@azure/msal-react';
import React, { ReactNode, useEffect } from 'react';
import { loginRedirectRequest } from '../../authConfig';

interface AuthenticationTemplateProps {
  children: ReactNode;
  onAuthenticated?: (account: AccountInfo) => void;
}

const AuthenticationTemplate: React.FC<AuthenticationTemplateProps> = ({ children, onAuthenticated }) => {
  const { instance, accounts } = useMsal();

  useEffect(() => {
    const handleAuth = async () => {
      try {
        // Try to handle any existing redirect promise first
        const result = await instance.handleRedirectPromise();

        if (result?.account) {
          if (onAuthenticated) {
            onAuthenticated(result.account);
          }
          return;
        }

        // If we're not authenticated, immediately redirect to B2C login
        if (accounts.length === 0) {
          await instance.loginRedirect(loginRedirectRequest);
          return;
        }

        // If we have an account but no result, call the callback
        if (onAuthenticated && accounts[0]) {
          onAuthenticated(accounts[0]);
        }
      } catch (error) {
        if (error instanceof BrowserAuthError && error.errorCode === 'interaction_in_progress') {
          try {
            const result = await instance.handleRedirectPromise();
            if (result?.account && onAuthenticated) {
              onAuthenticated(result.account);
            }
          } catch (redirectError) {
            console.error('Error handling redirect:', redirectError);
          }
        } else {
          console.error('Authentication error:', error);
          // If there's an error and user is not authenticated, redirect to login
          if (accounts.length === 0) {
            await instance.loginRedirect(loginRedirectRequest);
          }
        }
      }
    };

    handleAuth();
  }, [instance, accounts, onAuthenticated]);

  // Show nothing while authentication is in progress
  if (accounts.length === 0) {
    return null;
  }

  return <>{children}</>;
};

export default AuthenticationTemplate; 