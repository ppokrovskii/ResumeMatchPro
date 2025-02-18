/* eslint-disable no-console */
import { AccountInfo, IPublicClientApplication, SilentRequest } from '@azure/msal-browser';
import { apiTokenRequest, interactiveRequest } from '../authConfig';

interface CachedToken {
    accessToken: string;
    expiresAt: number;
    account: AccountInfo;
    scopes: string[];
}

// Add interface for MSAL error
interface MsalError {
    errorCode: string;
    errorMessage: string;
}

class TokenService {
    private static instance: TokenService;
    private tokenCache: Map<string, CachedToken> = new Map();
    private refreshInProgress: Map<string, Promise<string>> = new Map();

    private constructor() { }

    public static getInstance(): TokenService {
        if (!TokenService.instance) {
            TokenService.instance = new TokenService();
        }
        return TokenService.instance;
    }

    private getCacheKey(account: AccountInfo, scopes: string[]): string {
        return `${account.homeAccountId}:${scopes.sort().join(',')}`;
    }

    private isTokenExpired(token: CachedToken): boolean {
        // Consider token expired 5 minutes before actual expiration
        return Date.now() >= token.expiresAt - 5 * 60 * 1000;
    }

    private async refreshToken(
        instance: IPublicClientApplication,
        account: AccountInfo,
        scopes: string[],
        forceRefresh: boolean = false
    ): Promise<string> {
        try {
            const request: SilentRequest = {
                account,
                scopes,
                forceRefresh
            };

            const response = await instance.acquireTokenSilent(request);

            // Cache the new token
            this.tokenCache.set(this.getCacheKey(account, scopes), {
                accessToken: response.accessToken,
                expiresAt: response.expiresOn?.getTime() || Date.now() + 3600 * 1000,
                account,
                scopes
            });

            return response.accessToken;
        } catch (error) {
            const msalError = error as MsalError;
            if (msalError.errorCode === 'interaction_required' || msalError.errorCode === 'consent_required') {
                // If it's an API scope, first ensure we have valid basic scopes
                if (scopes.some(scope => scope.includes('resumematchpro-api'))) {
                    try {
                        // Try to refresh the basic token first
                        await this.refreshToken(instance, account, ['openid', 'profile', 'offline_access'], true);
                    } catch (basicError) {
                        console.log('Failed to refresh basic token, proceeding with interactive login');
                    }
                }

                // Fallback to interactive login
                console.log('Token refresh failed, proceeding with interactive login');
                const response = await instance.acquireTokenPopup({
                    ...interactiveRequest,
                    scopes,
                    account
                });

                // Cache the new token
                this.tokenCache.set(this.getCacheKey(account, scopes), {
                    accessToken: response.accessToken,
                    expiresAt: response.expiresOn?.getTime() || Date.now() + 3600 * 1000,
                    account,
                    scopes
                });

                return response.accessToken;
            }
            throw error;
        }
    }

    public async getAccessToken(
        instance: IPublicClientApplication,
        account: AccountInfo,
        scopes: string[] = apiTokenRequest.scopes
    ): Promise<string> {
        const cacheKey = this.getCacheKey(account, scopes);
        const cachedToken = this.tokenCache.get(cacheKey);

        // Check if there's already a refresh in progress for this token
        const existingRefresh = this.refreshInProgress.get(cacheKey);
        if (existingRefresh) {
            return existingRefresh;
        }

        // If we have a valid cached token, use it
        if (cachedToken && !this.isTokenExpired(cachedToken)) {
            return cachedToken.accessToken;
        }

        try {
            // Start a new refresh
            const refreshPromise = this.refreshToken(instance, account, scopes, !cachedToken);
            this.refreshInProgress.set(cacheKey, refreshPromise);

            const token = await refreshPromise;
            return token;
        } finally {
            // Clean up the refresh promise
            this.refreshInProgress.delete(cacheKey);
        }
    }

    public async getAuthHeaders(
        instance: IPublicClientApplication,
        account: AccountInfo
    ): Promise<HeadersInit> {
        console.log('Getting auth headers for:', {
            account: account.username,
            scopes: apiTokenRequest.scopes
        });

        const token = await this.getAccessToken(instance, account);

        console.log('Auth headers prepared:', {
            account: account.username,
            hasToken: !!token,
            tokenLength: token?.length
        });

        return {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };
    }

    public clearCache(): void {
        this.tokenCache.clear();
        this.refreshInProgress.clear();
    }
}

export const tokenService = TokenService.getInstance(); 