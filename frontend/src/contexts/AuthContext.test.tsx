import { msalInstance } from './AuthContext';

describe('AuthContext', () => {
  it('initializes MSAL instance', () => {
    expect(msalInstance).toBeDefined();
  });
}); 