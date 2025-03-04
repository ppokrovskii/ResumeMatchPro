import { AccountInfo, IdTokenClaims, InteractionStatus, IPublicClientApplication } from '@azure/msal-browser';
import { useMsal } from '@azure/msal-react';
import { notification } from 'antd';
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { createOrUpdateUser } from '../services/userService';

interface ExtendedIdTokenClaims extends IdTokenClaims {
  newUser?: boolean;
  isNewUser?: boolean;
  extension_IsAdmin?: boolean;
}

export async function registerUser(claims: ExtendedIdTokenClaims, account: AccountInfo, instance: IPublicClientApplication) {
  try {
    const result = await createOrUpdateUser(account, instance);
    return result;
  } catch (error) {
    console.error('Error registering user:', error);
    throw error;
  }
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
  const [hasShownWelcome, setHasShownWelcome] = useState(false);

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

          // First check if the token is expired
          const tokenExpirationCheck = await instance.acquireTokenSilent({
            account: account,
            scopes: ["openid", "profile"]
          }).catch(() => null);

          // If token is expired or not present, redirect to login immediately
          if (!tokenExpirationCheck) {
            // Silent token acquisition failed, redirecting to login
            setUser(null);
            await instance.loginRedirect();
            return;
          }

          const claims = tokenExpirationCheck.idTokenClaims as ExtendedIdTokenClaims;
          const userIsNew = claims.newUser || false;

          // Check if we've already registered this user
          const registeredUsers = JSON.parse(localStorage.getItem('registeredUsers') || '[]');
          const isAlreadyRegistered = registeredUsers.includes(claims.sub);

          // If it's a new user and we haven't registered them yet
          if (userIsNew && !isAlreadyRegistered) {
            try {
              await registerUser(claims, account, instance);
              registeredUsers.push(claims.sub);
              localStorage.setItem('registeredUsers', JSON.stringify(registeredUsers));
              if (!hasShownWelcome) {
                notification.success({
                  message: 'Welcome to Resume Match Pro!',
                  description: 'Thank you for joining us. Get started by uploading your CV or job description.',
                  duration: 10,
                  placement: 'topRight'
                });
                setHasShownWelcome(true);
              }
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
          // Clear user state and redirect to login
          setUser(null);
          await instance.loginRedirect();
        }
      } else {
        setUser(null);
      }
    };

    if (inProgress === InteractionStatus.None) {
      updateUserInfo();
    }
  }, [instance, accounts, inProgress, hasShownWelcome]);

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