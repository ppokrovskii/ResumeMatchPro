import { AccountInfo, IdTokenClaims, InteractionStatus, IPublicClientApplication } from '@azure/msal-browser';
import { useMsal } from '@azure/msal-react';
import { notification } from 'antd';
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

interface ExtendedIdTokenClaims extends IdTokenClaims {
  newUser?: boolean;
  isNewUser?: boolean;
  extension_IsAdmin?: boolean;
}

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

// Helper function to construct API URLs
const getApiUrl = (path: string) => {
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return `${API_BASE_URL}/${cleanPath}`;
};

export async function registerUser(claims: ExtendedIdTokenClaims, account: AccountInfo, instance: IPublicClientApplication) {
  try {
    // Get the token first
    const response = await instance.acquireTokenSilent({
      account,
      scopes: ["openid", "profile", "https://resumematchprodev.onmicrosoft.com/resumematchpro-api/Files.ReadWrite"]
    });

    const token = response.accessToken;

    // Make the API call with the token
    const apiResponse = await fetch(getApiUrl('users'), {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      credentials: 'include',
      body: JSON.stringify({
        userId: claims.sub,
        email: account.username,
        name: account.name
      })
    });

    if (!apiResponse.ok) {
      // If it's a conflict (user exists), that's fine
      if (apiResponse.status !== 409) {
        throw new Error(`Failed to register user: ${apiResponse.statusText}`);
      }
    }

    const result = await apiResponse.json();

    // Show welcome message only on successful registration (not on 409 conflict)
    if (apiResponse.ok && apiResponse.status !== 409) {
      notification.success({
        message: 'Welcome to Resume Match Pro!',
        description: 'Thank you for joining us. Get started by uploading your CV or job description.',
        duration: 10,
        placement: 'topRight'
      });
    }

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
          const userIsNew = claims.newUser || false;

          // If it's a new user, register them
          if (userIsNew) {
            try {
              await registerUser(claims, account, instance);
              // Show welcome message when we detect a new user from token claims
              notification.success({
                message: 'Welcome to Resume Match Pro!',
                description: 'Thank you for joining us. Get started by uploading your CV or job description.',
                duration: 10,
                placement: 'topRight'
              });
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