export const useMsal = jest.fn(() => ({
  instance: {
    loginRedirect: jest.fn(),
    logoutRedirect: jest.fn(),
    handleRedirectPromise: jest.fn(),
    getAllAccounts: jest.fn(() => []),
    getActiveAccount: jest.fn(),
    setActiveAccount: jest.fn(),
  },
  accounts: [],
  inProgress: "none",
}));

export const MsalProvider = ({ children }: { children: React.ReactNode }) => children;

export const MsalAuthenticationTemplate = ({ children }: { children: React.ReactNode }) => children;

export const UnauthenticatedTemplate = ({ children }: { children: React.ReactNode }) => children;

export const AuthenticatedTemplate = ({ children }: { children: React.ReactNode }) => children; 