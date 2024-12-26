export const PublicClientApplication = jest.fn().mockImplementation(() => ({
  initialize: jest.fn().mockResolvedValue(undefined),
  handleRedirectPromise: jest.fn(),
  getActiveAccount: jest.fn(),
  getAllAccounts: jest.fn().mockReturnValue([]),
  setActiveAccount: jest.fn(),
}));

export class AccountInfo {
  homeAccountId: string = '';
  localAccountId: string = '';
  environment: string = '';
  tenantId: string = '';
  username: string = '';

  constructor(init: Partial<AccountInfo>) {
    Object.assign(this, init);
  }
} 