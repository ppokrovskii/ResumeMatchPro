import { Configuration } from '@azure/msal-browser';

const baseUrl = process.env.REACT_APP_BASE_URL || 'provide_base_url';

export const msalConfig: Configuration = {
  auth: {
    clientId: 'test-client-id',
    authority: 'https://test.authority.com',
    redirectUri: baseUrl,
    postLogoutRedirectUri: baseUrl,
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
};

export const loginRequest = {
  scopes: ['openid'],
};

export const policies = {
  signUpSignIn: 'B2C_1_signupsignin',
  passwordReset: 'B2C_1_passwordreset',
}; 