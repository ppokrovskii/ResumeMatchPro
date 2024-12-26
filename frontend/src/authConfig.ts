import { Configuration } from '@azure/msal-browser';

// B2C Policy/User Flow names
const b2cPolicies = {
  signUpSignIn: "B2C_1_signupsignin",
  passwordReset: "B2C_1_passwordreset"
};

// B2C Endpoints
const b2cAuth = {
  tenant: process.env.REACT_APP_B2C_TENANT || "resumematchprodev",
  clientId: process.env.REACT_APP_B2C_CLIENT_ID || "REACT_APP_B2C_CLIENT_ID not set",
  authorityDomain: process.env.REACT_APP_B2C_AUTHORITY_DOMAIN || "resumematchprodev.b2clogin.com",
};

// Authority URLs - Using the exact format from Azure Portal
const authorityBase = `https://${b2cAuth.authorityDomain}/${b2cAuth.tenant}.onmicrosoft.com`;

// Get the base URL from environment or window.location
const baseUrl = process.env.REACT_APP_BASE_URL || window.location.origin;
console.log('Auth configuration:', {
  baseUrl,
  windowOrigin: window.location.origin,
  environment: process.env.NODE_ENV,
  b2cTenant: b2cAuth.tenant,
  authorityDomain: b2cAuth.authorityDomain
});

const redirectUri = `${baseUrl}/auth-callback`;

export const msalConfig: Configuration = {
  auth: {
    clientId: b2cAuth.clientId,
    authority: `${authorityBase}/${b2cPolicies.signUpSignIn}`,
    knownAuthorities: [b2cAuth.authorityDomain],
    redirectUri: redirectUri,
    postLogoutRedirectUri: baseUrl,
  },
  cache: {
    cacheLocation: 'localStorage',
    storeAuthStateInCookie: true,
  }
};

// Login request with implicit flow
export const loginRequest = {
  scopes: ['openid'],
  prompt: 'select_account',
  responseType: 'token id_token'
};

// Redirect request with implicit flow
export const loginRedirectRequest = {
  ...loginRequest,
  prompt: 'select_account'
};

// Signup request with implicit flow
export const signUpRedirectRequest = {
  ...loginRequest,
  prompt: 'create'
};

export const policies = b2cPolicies; 