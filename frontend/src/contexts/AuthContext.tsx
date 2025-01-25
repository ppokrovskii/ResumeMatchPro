import { InteractionStatus } from '@azure/msal-browser';
import { useMsal } from '@azure/msal-react';
import React, { createContext, useCallback, useEffect, useMemo, useState } from 'react';

export interface AuthContextType {
  isAuthenticated: boolean;
  user: {
    name: string;
    isAdmin: boolean;
  } | null;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  isInitialized: boolean;
}

const defaultContext: AuthContextType = {
  isAuthenticated: false,
  user: null,
  login: async () => { },
  logout: async () => { },
  isInitialized: false
};

export const AuthContext = createContext<AuthContextType>(defaultContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { instance, accounts, inProgress } = useMsal();
  const [user, setUser] = useState<AuthContextType['user']>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        await instance.initialize();
        setIsInitialized(true);
      } catch (error) {
        console.error('Failed to initialize MSAL:', error);
      }
    };

    initializeAuth();
  }, [instance]);

  useEffect(() => {
    if (accounts.length > 0) {
      const account = accounts[0];
      setUser({
        name: account.name || '',
        isAdmin: false, // Set based on your requirements
      });
    } else {
      setUser(null);
    }
  }, [accounts]);

  const login = useCallback(async () => {
    if (!isInitialized || inProgress !== InteractionStatus.None) return;
    await instance.loginRedirect();
  }, [instance, isInitialized, inProgress]);

  const logout = useCallback(async () => {
    if (!isInitialized || inProgress !== InteractionStatus.None) return;
    await instance.logoutRedirect();
  }, [instance, isInitialized, inProgress]);

  const contextValue = useMemo(() => ({
    isAuthenticated: accounts.length > 0 && inProgress === InteractionStatus.None,
    user,
    login,
    logout,
    isInitialized
  }), [accounts.length, inProgress, user, login, logout, isInitialized]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}; 