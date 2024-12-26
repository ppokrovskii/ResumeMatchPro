import { msalInstance } from './AuthContext';

jest.mock('@azure/msal-browser', () => ({
  PublicClientApplication: jest.fn().mockImplementation(() => ({
    initialize: jest.fn().mockResolvedValue(undefined),
    handleRedirectPromise: jest.fn().mockResolvedValue(null),
    getAllAccounts: jest.fn().mockReturnValue([]),
    getActiveAccount: jest.fn().mockReturnValue(null),
    setActiveAccount: jest.fn(),
    addEventCallback: jest.fn(),
  }))
}));

describe('AuthContext', () => {
  it('initializes MSAL instance', () => {
    expect(msalInstance).toBeDefined();
    expect(msalInstance.initialize).toBeDefined();
    expect(msalInstance.handleRedirectPromise).toBeDefined();
  });
}); 