export const msalConfig = {
  auth: {
    clientId: 'test-client-id',
    authority: 'test-authority',
    knownAuthorities: ['test-authority'],
    redirectUri: 'http://localhost:3000',
    postLogoutRedirectUri: 'http://localhost:3000',
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: true,
  }
};

export const loginRequest = {
  scopes: ['openid'],
  prompt: 'select_account',
  responseType: 'token id_token'
};

export const policies = {
  signUpSignIn: "B2C_1_signupsignin",
  passwordReset: "B2C_1_passwordreset"
}; 