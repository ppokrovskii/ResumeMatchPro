/* eslint-disable no-console */
import { InteractionRequiredAuthError, InteractionStatus } from '@azure/msal-browser';
import { useMsal } from '@azure/msal-react';
import React, { useContext, useEffect } from 'react';
import { AuthContext } from '../../contexts/AuthContext';

interface AuthenticationTemplateProps {
  children: React.ReactNode;
  onAuthenticated: (user: { name: string; isAdmin: boolean }) => void;
}

const AuthenticationTemplate: React.FC<AuthenticationTemplateProps> = ({
  children,
  onAuthenticated
}) => {
  const { isAuthenticated, user, login } = useContext(AuthContext);
  const { inProgress } = useMsal();

  useEffect(() => {
    const initiateLogin = async () => {
      if (!isAuthenticated && inProgress === InteractionStatus.None) {
        try {
          await login();
        } catch (error) {
          if (!(error instanceof InteractionRequiredAuthError)) {
            console.error('Login error:', error);
          }
        }
      }
    };

    initiateLogin();
  }, [isAuthenticated, login, inProgress]);

  useEffect(() => {
    if (isAuthenticated && user) {
      onAuthenticated(user);
    }
  }, [isAuthenticated, user, onAuthenticated]);

  if (!isAuthenticated || !user || inProgress !== InteractionStatus.None) {
    return <div>Loading...</div>;
  }

  return <>{children}</>;
};

export default AuthenticationTemplate; 