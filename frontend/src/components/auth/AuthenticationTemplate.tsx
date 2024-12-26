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
      try {
        // Try to handle any existing redirect promise first
        const result = await instance.handleRedirectPromise();
        
        if (result?.account) {
          // If we got a result, the redirect was handled successfully
          if (onAuthenticated) {
            onAuthenticated(result.account);
          }
          return;
        }

        // If we're not authenticated, initiate login
        if (accounts.length === 0) {
          await instance.loginRedirect();
        } else if (onAuthenticated && accounts[0]) {
          // If we're already authenticated, call the callback with the first account
          onAuthenticated(accounts[0]);
        }
      } catch (error) {
        if (error instanceof BrowserAuthError && error.errorCode === 'interaction_in_progress') {
          // If there's an interaction in progress, wait for it to complete
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
        }
      }
    };

    handleAuth();
  }, [instance, accounts, onAuthenticated]);

  // Only render children if authenticated
  if (accounts.length === 0) {
    return null;
  }

  return <>{children}</>;
};

export default AuthenticationTemplate; 