import React, { ReactNode } from 'react';
import { useMsal } from '@azure/msal-react';
import { AccountInfo } from '@azure/msal-browser';

interface AuthenticationTemplateProps {
  children: ReactNode;
  onAuthenticated?: (account: AccountInfo) => void;
}

const AuthenticationTemplate: React.FC<AuthenticationTemplateProps> = ({ children, onAuthenticated }) => {
  const { accounts } = useMsal();
  
  React.useEffect(() => {
    if (accounts.length > 0 && onAuthenticated) {
      onAuthenticated(accounts[0]);
    }
  }, [accounts, onAuthenticated]);

  return <>{children}</>;
};

export default AuthenticationTemplate; 