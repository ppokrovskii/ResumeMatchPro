/* eslint-disable no-console */
import { Configuration } from '@azure/msal-browser';



// B2C Endpoints
const b2cAuth = {
  tenant: process.env.REACT_APP_B2C_TENANT || "resumematchprodev",
  clientId: process.env.REACT_APP_FRONTEND_CLIENT_ID || "42517ab6-e124-413b-8e1f-ba4d38e13c9c",
  authorityDomain: process.env.REACT_APP_B2C_AUTHORITY_DOMAIN || "resumematchprodev.b2clogin.com",
  backendClientId: process.env.REACT_APP_BACKEND_CLIENT_ID || "50b21c0f-f505-4d30-97f9-033b52e9425c"
};



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
  'offline_access',
  b2cAuth.clientId,  // required to get the access token
  // `https://resumematchprodev.onmicrosoft.com/resumematchpro-api/Files.ReadWrite`
];

const apiScopes = [
  `api://${b2cAuth.backendClientId}/Files.ReadWrite`
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