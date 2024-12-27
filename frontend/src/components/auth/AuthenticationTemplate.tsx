/* eslint-disable no-console */
import { AccountInfo, BrowserAuthError } from '@azure/msal-browser';
import { useMsal } from '@azure/msal-react';
import React, { ReactNode, useEffect } from 'react';

interface AuthenticationTemplateProps {
  children: ReactNode;
  onAuthenticated?: (account: AccountInfo) => void;
}

const AuthenticationTemplate: React.FC<AuthenticationTemplateProps> = ({ children, onAuthenticated }) => {
  const { instance, accounts } = useMsal();
  
  useEffect(() => {
    const handleAuth = async () => {
      console.log('Starting authentication flow...', {
        accountsCount: accounts.length,
        hasOnAuthenticated: !!onAuthenticated
      });

      try {
        // Try to handle any existing redirect promise first
        console.log('Attempting to handle redirect promise...');
        const result = await instance.handleRedirectPromise();
        
        if (result?.account) {
          console.log('Redirect handled successfully with account:', {
            username: result.account.username,
            homeAccountId: result.account.homeAccountId
          });
          
          if (onAuthenticated) {
            console.log('Calling onAuthenticated callback with redirect result');
            onAuthenticated(result.account);
          }
          return;
        }

        console.log('No redirect result, checking authentication state...', {
          accountsCount: accounts.length
        });

        // If we're not authenticated, initiate login
        if (accounts.length === 0) {
          console.log('No accounts found, initiating login redirect...');
          await instance.loginRedirect();
        } else if (onAuthenticated && accounts[0]) {
          console.log('Already authenticated, calling callback with existing account:', {
            username: accounts[0].username,
            homeAccountId: accounts[0].homeAccountId
          });
          onAuthenticated(accounts[0]);
        }
      } catch (error) {
        if (error instanceof BrowserAuthError && error.errorCode === 'interaction_in_progress') {
          console.log('Interaction in progress detected, waiting for completion...');
          try {
            console.log('Attempting to handle existing redirect...');
            const result = await instance.handleRedirectPromise();
            if (result?.account && onAuthenticated) {
              console.log('Successfully handled existing redirect:', {
                username: result.account.username,
                homeAccountId: result.account.homeAccountId
              });
              onAuthenticated(result.account);
            } else {
              console.log('No account found after handling redirect', {
                hasResult: !!result,
                hasAccount: !!result?.account
              });
            }
          } catch (redirectError) {
            console.error('Error handling redirect during interaction:', {
              error: redirectError,
              errorType: redirectError instanceof Error ? redirectError.constructor.name : typeof redirectError,
              errorMessage: redirectError instanceof Error ? redirectError.message : 'Unknown error'
            });
          }
        } else {
          console.error('Authentication error:', {
            error,
            errorType: error instanceof Error ? error.constructor.name : typeof error,
            errorMessage: error instanceof Error ? error.message : 'Unknown error',
            errorCode: error instanceof BrowserAuthError ? error.errorCode : undefined
          });
        }
      }
    };

    handleAuth();
  }, [instance, accounts, onAuthenticated]);

  // Only render children if authenticated
  if (accounts.length === 0) {
    console.log('No accounts available, not rendering children');
    return null;
  }

  console.log('Authenticated, rendering children');
  return <>{children}</>;
};

export default AuthenticationTemplate; 