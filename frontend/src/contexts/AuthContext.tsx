import React, { createContext, useContext, useEffect } from 'react';
import { PublicClientApplication, EventType, AuthenticationResult } from '@azure/msal-browser';
import { msalConfig } from '../authConfig';

// Create MSAL instance
export const msalInstance = new PublicClientApplication(msalConfig);

// Initialize MSAL
msalInstance.initialize().then(() => {
  if (!msalInstance.getActiveAccount() && msalInstance.getAllAccounts().length > 0) {
    msalInstance.setActiveAccount(msalInstance.getAllAccounts()[0]);
  }
});

// Event handling
msalInstance.addEventCallback((event) => {
  if (
    event.eventType === EventType.LOGIN_SUCCESS && 
    event.payload && 
    'account' in event.payload
  ) {
    const payload = event.payload as AuthenticationResult;
    console.log('Login successful');
    if (payload.account) {
      msalInstance.setActiveAccount(payload.account);
    }
  }
});

export const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext); 