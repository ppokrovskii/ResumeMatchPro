/* eslint-disable no-console */
import { Configuration } from '@azure/msal-browser';

// B2C Endpoints
const b2cAuth = {
  tenant: process.env.REACT_APP_B2C_TENANT,
  clientId: process.env.REACT_APP_FRONTEND_CLIENT_ID,
  authorityDomain: process.env.REACT_APP_B2C_AUTHORITY_DOMAIN,
  backendClientId: process.env.REACT_APP_BACKEND_CLIENT_ID
};

if (!b2cAuth.tenant || !b2cAuth.clientId || !b2cAuth.authorityDomain || !b2cAuth.backendClientId) {
  throw new Error('Required B2C configuration is missing');
}

// Authority URLs
const authorityBase = `https://${b2cAuth.authorityDomain}/${b2cAuth.tenant}.onmicrosoft.com`;

// B2C Policy/User Flow names
const b2cPolicies = {
  signUpSignIn: {
    name: "B2C_1_signupsignin",
    authority: `${authorityBase}/B2C_1_signupsignin/v2.0`
  },
  passwordReset: {
    name: "B2C_1_passwordreset",
    authority: `${authorityBase}/B2C_1_passwordreset/v2.0`
  }
};

// Get the base URL from environment
const baseUrl = process.env.REACT_APP_BASE_URL;
if (!baseUrl) {
  throw new Error('REACT_APP_BASE_URL environment variable is not set');
}

// Construct redirect URI with trailing slash
const redirectUri = `${baseUrl}/auth-callback/`;

// API Scopes - separate login and API scopes
const loginScopes = [
  'openid',
  'profile',
  'offline_access'
];

// Construct API scope using the tenant from environment
const apiScopes = [
  `https://${b2cAuth.tenant}.onmicrosoft.com/resumematchpro-api/Files.ReadWrite`
];

// MSAL Configuration
export const msalConfig: Configuration = {
  auth: {
    clientId: b2cAuth.clientId,
    authority: b2cPolicies.signUpSignIn.authority,
    redirectUri: redirectUri,
    knownAuthorities: [b2cAuth.authorityDomain],
    postLogoutRedirectUri: baseUrl,
    navigateToLoginRequestUrl: true
  },
  cache: {
    cacheLocation: "localStorage",
    storeAuthStateInCookie: true,
    secureCookies: true
  },
  system: {
    allowNativeBroker: false,
    windowHashTimeout: 60000,
    iframeHashTimeout: 6000,
    loadFrameTimeout: 0,
    asyncPopups: false
  }
};

// Login request (for B2C authentication)
export const loginRequest = {
  scopes: loginScopes,
};

// Token request for API access (separate from login)
export const apiTokenRequest = {
  scopes: apiScopes,
  forceRefresh: false
};

// Interactive request (for login)
export const interactiveRequest = {
  scopes: loginScopes,
  prompt: 'select_account'
};

// Redirect request
export const loginRedirectRequest = {
  ...interactiveRequest
};

// Signup request
export const signUpRedirectRequest = {
  ...interactiveRequest,
  prompt: 'create'
};

export const policies = b2cPolicies; 