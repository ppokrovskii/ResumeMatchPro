/* eslint-disable no-console */
import { AccountInfo, IPublicClientApplication, InteractionRequiredAuthError } from '@azure/msal-browser';
import { apiTokenRequest, interactiveRequest } from '../authConfig';

interface CachedToken {
    accessToken: string;
    expiresAt: number;
    account: AccountInfo;
    scopes: string[];
}

class TokenService {
    private static instance: TokenService;
    private tokenCache: Map<string, CachedToken> = new Map();

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

    public async getAccessToken(
        instance: IPublicClientApplication,
        account: AccountInfo,
        scopes: string[] = apiTokenRequest.scopes
    ): Promise<string> {
        const cacheKey = this.getCacheKey(account, scopes);
        const cachedToken = this.tokenCache.get(cacheKey);

        if (cachedToken && !this.isTokenExpired(cachedToken)) {
            return cachedToken.accessToken;
        }

        try {
            // Always try silent token acquisition first
            const response = await instance.acquireTokenSilent({
                account,
                scopes,
                forceRefresh: !cachedToken // Force refresh if no cached token
            });

            // Cache the new token
            this.tokenCache.set(cacheKey, {
                accessToken: response.accessToken,
                expiresAt: response.expiresOn?.getTime() || Date.now() + 3600 * 1000,
                account,
                scopes
            });

            return response.accessToken;
        } catch (error) {
            if (error instanceof InteractionRequiredAuthError) {
                // For API scopes, first ensure we have the basic scopes
                if (scopes.some(scope => scope.includes('resumematchpro-api'))) {
                    try {
                        // First get/refresh the basic token
                        await instance.acquireTokenSilent({
                            account,
                            scopes: ['openid', 'profile', 'offline_access'],
                            forceRefresh: true
                        });
                    } catch (basicError) {
                        // If basic token refresh fails, try interactive
                        await instance.acquireTokenPopup({
                            scopes: ['openid', 'profile', 'offline_access']
                        });
                    }
                }

                // Now try to get the API token
                const response = await instance.acquireTokenPopup({
                    ...interactiveRequest,
                    scopes
                });

                // Cache the new token
                this.tokenCache.set(cacheKey, {
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
    }
}

export const tokenService = TokenService.getInstance(); 