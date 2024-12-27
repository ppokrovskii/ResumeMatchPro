import React, { createContext, useContext, useEffect, useState } from 'react';
import { useMsal } from '@azure/msal-react';
import { AccountInfo, PublicClientApplication } from '@azure/msal-browser';
import { msalConfig } from '../authConfig';

// Create MSAL instance
export const msalInstance = new PublicClientApplication(msalConfig);

// Default initialize MSAL
msalInstance.initialize().then(() => {
  // Set active account if available
  if (!msalInstance.getActiveAccount() && msalInstance.getAllAccounts().length > 0) {
    msalInstance.setActiveAccount(msalInstance.getAllAccounts()[0]);
  }
});

interface AuthContextType {
  isAuthenticated: boolean;
  account: AccountInfo | null;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  account: null,
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { accounts } = useMsal();
  const [account, setAccount] = useState<AccountInfo | null>(null);

  useEffect(() => {
    // Handle account changes
    const currentAccount = accounts[0] || null;
    if (currentAccount && (!account || account.homeAccountId !== currentAccount.homeAccountId)) {
      console.error('Account changed:', currentAccount.username);
      setAccount(currentAccount);
    } else if (!currentAccount && account) {
      console.error('User signed out');
      setAccount(null);
    }
  }, [accounts, account]);

  const value = {
    isAuthenticated: !!account,
    account,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext; 