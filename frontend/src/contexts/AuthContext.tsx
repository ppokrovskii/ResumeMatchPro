import { AccountInfo, IdTokenClaims, InteractionStatus } from '@azure/msal-browser';
import { useMsal } from '@azure/msal-react';
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

interface ExtendedIdTokenClaims extends IdTokenClaims {
  newUser?: boolean;
  isNewUser?: boolean;
  extension_IsAdmin?: boolean;
}

const KNOWN_USERS_KEY = 'rmp_known_users';
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

// Helper function to construct API URLs
const getApiUrl = (path: string) => {
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return `${API_BASE_URL}/${cleanPath}`;
};

async function registerUser(claims: ExtendedIdTokenClaims, account: AccountInfo) {
  try {
    const response = await fetch(getApiUrl('users'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userId: claims.sub,
        email: account.username,
        name: account.name,
        isAdmin: claims.extension_IsAdmin || false,
        filesLimit: 20,        // Default limit
        matchingLimit: 100     // Default limit
      })
    });

    if (!response.ok) {
      // If it's a conflict (user exists), that's fine
      if (response.status !== 409) {
        throw new Error(`Failed to register user: ${response.statusText}`);
      }
    }

    return await response.json();
  } catch (error) {
    console.error('Error registering user:', error);
    throw error;
  }
}

function isNewUser(userId: string): boolean {
  const knownUsers = JSON.parse(localStorage.getItem(KNOWN_USERS_KEY) || '[]');
  if (!knownUsers.includes(userId)) {
    knownUsers.push(userId);
    localStorage.setItem(KNOWN_USERS_KEY, JSON.stringify(knownUsers));
    return true;
  }
  return false;
}

export interface AuthContextType {
  isAuthenticated: boolean;
  user: {
    name: string;
    isAdmin: boolean;
    idTokenClaims?: ExtendedIdTokenClaims;
    account?: AccountInfo;
    homeAccountId?: string;
    isNewUser?: boolean;
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

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

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
    const updateUserInfo = async () => {
      if (accounts.length > 0) {
        const account = accounts[0];
        try {
          const currentAccount = instance.getActiveAccount();
          if (!currentAccount) {
            instance.setActiveAccount(account);
          }

          const response = await instance.acquireTokenSilent({
            account: account,
            scopes: ["openid", "profile"]
          });

          const claims = response.idTokenClaims as ExtendedIdTokenClaims;
          const userId = claims.sub || account.localAccountId;
          const userIsNew = isNewUser(userId);

          // If it's a new user, register them
          if (userIsNew) {
            try {
              await registerUser(claims, account);
            } catch (error) {
              console.error('Failed to register new user:', error);
            }
          }

          setUser({
            name: account.name || '',
            isAdmin: claims?.extension_IsAdmin || false,
            idTokenClaims: claims,
            account: account,
            homeAccountId: account.homeAccountId,
            isNewUser: userIsNew
          });
        } catch (error) {
          console.error('Failed to get token claims:', error);
          // Try to get a new token if silent acquisition fails
          try {
            const response = await instance.acquireTokenPopup({
              account: account,
              scopes: ["openid", "profile"]
            });

            const claims = response.idTokenClaims as ExtendedIdTokenClaims;
            setUser({
              name: account.name || '',
              isAdmin: claims?.extension_IsAdmin || false,
              idTokenClaims: claims,
              account: account,
              homeAccountId: account.homeAccountId,
              isNewUser: false
            });
          } catch (popupError) {
            console.error('Failed to get token via popup:', popupError);
            setUser({
              name: account.name || '',
              isAdmin: false,
              account: account,
              homeAccountId: account.homeAccountId,
              isNewUser: false
            });
          }
        }
      } else {
        setUser(null);
      }
    };

    if (inProgress === InteractionStatus.None) {
      updateUserInfo();
    }
  }, [instance, accounts, inProgress]);

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