import { InteractionStatus, IPublicClientApplication } from '@azure/msal-browser';

export const mockMsalInstance: IPublicClientApplication = {
    acquireTokenSilent: jest.fn().mockResolvedValue({
        idTokenClaims: { name: 'Test User' }
    }),
    acquireTokenPopup: jest.fn().mockResolvedValue({ idTokenClaims: {} }),
    acquireTokenRedirect: jest.fn().mockResolvedValue({ idTokenClaims: {} }),
    acquireTokenByCode: jest.fn().mockResolvedValue({ idTokenClaims: {} }),
    getAllAccounts: jest.fn().mockReturnValue([]),
    getAccountByHomeId: jest.fn(),
    getAccountByLocalId: jest.fn(),
    getAccountByUsername: jest.fn(),
    setActiveAccount: jest.fn(),
    getActiveAccount: jest.fn(),
    ssoSilent: jest.fn(),
    loginPopup: jest.fn(),
    loginRedirect: jest.fn(),
    logout: jest.fn(),
    logoutRedirect: jest.fn(),
    logoutPopup: jest.fn(),
    addEventCallback: jest.fn(),
    removeEventCallback: jest.fn(),
    addPerformanceCallback: jest.fn(),
    removePerformanceCallback: jest.fn(),
    enableAccountStorageEvents: jest.fn(),
    disableAccountStorageEvents: jest.fn(),
    getTokenCache: jest.fn(),
    setLogger: jest.fn(),
    getLogger: jest.fn(),
    setNavigationClient: jest.fn(),
    clearCache: jest.fn(),
    getAccount: jest.fn(),
    handleRedirectPromise: jest.fn().mockResolvedValue(null),
    initialize: jest.fn().mockResolvedValue(undefined),
    getConfiguration: jest.fn().mockReturnValue({
        auth: {
            authority: 'test-authority',
            redirectUri: 'test-redirect-uri',
        }
    }),
    initializeWrapperLibrary: jest.fn(),
    hydrateCache: jest.fn()
};

export const mockMsalState = {
    instance: mockMsalInstance,
    accounts: [],
    inProgress: InteractionStatus.None
};

export const mockAuthenticatedMsalState = {
    ...mockMsalState,
    accounts: [{
        name: 'Test User',
        homeAccountId: 'test-id',
        environment: 'test-env',
        tenantId: 'test-tenant',
        username: 'test@example.com',
    }]
};

export const mockMsalReactModule = {
    useMsal: () => mockMsalState,
    MsalProvider: jest.fn().mockImplementation(({ children }) => ({
        type: 'div',
        props: {
            'data-testid': 'msal-provider',
            children
        }
    }))
};

export const mockMsalBrowserModule = {
    InteractionStatus: {
        None: 'none',
        Startup: 'startup',
        Login: 'login',
        Logout: 'logout',
        AcquireToken: 'acquireToken',
        HandleRedirect: 'handleRedirect',
        SsoSilent: 'ssoSilent'
    }
}; 