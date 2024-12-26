const mockInstance = {
  initialize: jest.fn().mockImplementation(() => Promise.resolve()),
  handleRedirectPromise: jest.fn().mockImplementation(() => Promise.resolve(null)),
  loginRedirect: jest.fn().mockImplementation(() => Promise.resolve()),
  logoutRedirect: jest.fn().mockImplementation(() => Promise.resolve()),
  getAllAccounts: jest.fn().mockReturnValue([]),
  getActiveAccount: jest.fn().mockReturnValue(null),
  setActiveAccount: jest.fn(),
  addEventCallback: jest.fn(),
};

export const PublicClientApplication = jest.fn().mockImplementation(() => mockInstance);

export const InteractionType = {
  Redirect: 'redirect',
  Popup: 'popup',
  Silent: 'silent',
};

export const EventType = {
  LOGIN_SUCCESS: 'login_success',
  LOGIN_FAILURE: 'login_failure',
  LOGOUT_SUCCESS: 'logout_success',
  LOGOUT_FAILURE: 'logout_failure',
};

export const mockMsalInstance = mockInstance; 