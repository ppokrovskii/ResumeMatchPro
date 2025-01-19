/* eslint-disable no-console */
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

  useEffect(() => {
    if (!isAuthenticated) {
      login();
      return;
    }

    if (user) {
      onAuthenticated(user);
    }
  }, [isAuthenticated, user, login, onAuthenticated]);

  if (!isAuthenticated || !user) {
    return <div>Loading...</div>;
  }

  return <>{children}</>;
};

export default AuthenticationTemplate; 