import { AccountInfo, AuthenticationResult, IPublicClientApplication } from '@azure/msal-browser';
import { tokenService } from '../tokenService';

describe('TokenService', () => {
    let mockInstance: jest.Mocked<IPublicClientApplication>;
    let mockAccount: AccountInfo;

    beforeEach(() => {
        // Clear token cache before each test
        tokenService.clearCache();

        // Mock MSAL instance
        mockInstance = {
            acquireTokenSilent: jest.fn(),
            acquireTokenPopup: jest.fn(),
        } as unknown as jest.Mocked<IPublicClientApplication>;

        // Mock account info
        mockAccount = {
            homeAccountId: 'test-account-id',
            environment: 'test-environment',
            tenantId: 'test-tenant-id',
            username: 'test@example.com',
            localAccountId: 'test-local-id',
            name: 'Test User'
        };
    });

    it('should handle session expiration error and trigger interactive login', async () => {
        // Mock the session expiration error (AADB2C90077)
        const sessionExpirationError = {
            errorCode: 'interaction_required',
            errorMessage: 'User interaction is required'
        };

        // First call to acquireTokenSilent throws session expiration error
        mockInstance.acquireTokenSilent.mockRejectedValueOnce(sessionExpirationError);

        // Mock successful interactive login
        const mockAuthResult: AuthenticationResult = {
            authority: 'https://login.microsoftonline.com/common',
            uniqueId: 'test-unique-id',
            tenantId: 'test-tenant-id',
            scopes: ['test-scope'],
            account: mockAccount,
            idToken: 'test-id-token',
            idTokenClaims: {},
            accessToken: 'new-access-token',
            fromCache: false,
            expiresOn: new Date(Date.now() + 3600 * 1000),
            tokenType: 'Bearer',
            correlationId: 'test-correlation-id'
        };
        mockInstance.acquireTokenPopup.mockResolvedValueOnce(mockAuthResult);

        // Try to get a token
        const token = await tokenService.getAccessToken(mockInstance, mockAccount, ['test-scope']);

        // Verify that silent acquisition was attempted
        expect(mockInstance.acquireTokenSilent).toHaveBeenCalledWith({
            account: mockAccount,
            scopes: ['test-scope'],
            forceRefresh: true
        });

        // Verify that interactive login was triggered after silent failure
        expect(mockInstance.acquireTokenPopup).toHaveBeenCalledWith({
            scopes: ['test-scope'],
            account: mockAccount,
            prompt: 'select_account'
        });

        // Verify we got the new token
        expect(token).toBe('new-access-token');
    });

    it('should handle API scope refresh with expired session', async () => {
        const sessionExpirationError = {
            errorCode: 'interaction_required',
            errorMessage: 'User interaction is required'
        };

        // Mock failures for both basic and API scope silent refresh
        mockInstance.acquireTokenSilent
            .mockRejectedValueOnce(sessionExpirationError) // API scopes fail
            .mockRejectedValueOnce(sessionExpirationError); // Basic scopes fail

        // Mock successful interactive login
        const mockApiAuthResult: AuthenticationResult = {
            authority: 'https://login.microsoftonline.com/common',
            uniqueId: 'test-unique-id',
            tenantId: 'test-tenant-id',
            scopes: ['https://resumematchpro.onmicrosoft.com/resumematchpro-api/Files.ReadWrite'],
            account: mockAccount,
            idToken: 'test-id-token',
            idTokenClaims: {},
            accessToken: 'new-api-token',
            fromCache: false,
            expiresOn: new Date(Date.now() + 3600 * 1000),
            tokenType: 'Bearer',
            correlationId: 'test-correlation-id'
        };

        // Mock successful interactive login for both attempts
        mockInstance.acquireTokenPopup
            .mockResolvedValueOnce(mockApiAuthResult) // Basic scopes
            .mockResolvedValueOnce(mockApiAuthResult); // API scopes

        // Try to get a token for API scope
        const token = await tokenService.getAccessToken(
            mockInstance,
            mockAccount,
            ['https://resumematchpro.onmicrosoft.com/resumematchpro-api/Files.ReadWrite']
        );

        // Verify the sequence of calls
        expect(mockInstance.acquireTokenSilent).toHaveBeenCalledTimes(2);
        expect(mockInstance.acquireTokenPopup).toHaveBeenCalledTimes(2);
        expect(token).toBe('new-api-token');
    });

    it('should reuse token from cache if not expired', async () => {
        // Mock successful token acquisition
        const mockAuthResult: AuthenticationResult = {
            authority: 'https://login.microsoftonline.com/common',
            uniqueId: 'test-unique-id',
            tenantId: 'test-tenant-id',
            scopes: ['test-scope'],
            account: mockAccount,
            idToken: 'test-id-token',
            idTokenClaims: {},
            accessToken: 'cached-token',
            fromCache: false,
            expiresOn: new Date(Date.now() + 3600 * 1000),
            tokenType: 'Bearer',
            correlationId: 'test-correlation-id'
        };
        mockInstance.acquireTokenSilent.mockResolvedValueOnce(mockAuthResult);

        // Get token first time
        const token1 = await tokenService.getAccessToken(mockInstance, mockAccount, ['test-scope']);

        // Get token second time
        const token2 = await tokenService.getAccessToken(mockInstance, mockAccount, ['test-scope']);

        // Verify silent acquisition was called only once
        expect(mockInstance.acquireTokenSilent).toHaveBeenCalledTimes(1);
        expect(token1).toBe('cached-token');
        expect(token2).toBe('cached-token');
    });

    it('should prevent concurrent token refreshes for the same scope', async () => {
        // Mock a delayed token acquisition
        const mockAuthResult: AuthenticationResult = {
            authority: 'https://login.microsoftonline.com/common',
            uniqueId: 'test-unique-id',
            tenantId: 'test-tenant-id',
            scopes: ['test-scope'],
            account: mockAccount,
            idToken: 'test-id-token',
            idTokenClaims: {},
            accessToken: 'delayed-token',
            fromCache: false,
            expiresOn: new Date(Date.now() + 3600 * 1000),
            tokenType: 'Bearer',
            correlationId: 'test-correlation-id'
        };

        mockInstance.acquireTokenSilent.mockImplementationOnce(() =>
            new Promise(resolve => setTimeout(() => resolve(mockAuthResult), 100))
        );

        // Start multiple concurrent token requests
        const [token1, token2] = await Promise.all([
            tokenService.getAccessToken(mockInstance, mockAccount, ['test-scope']),
            tokenService.getAccessToken(mockInstance, mockAccount, ['test-scope'])
        ]);

        // Verify silent acquisition was called only once
        expect(mockInstance.acquireTokenSilent).toHaveBeenCalledTimes(1);
        expect(token1).toBe('delayed-token');
        expect(token2).toBe('delayed-token');
    });
}); 