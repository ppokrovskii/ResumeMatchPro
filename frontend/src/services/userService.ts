import { AccountInfo, IPublicClientApplication, InteractionRequiredAuthError } from '@azure/msal-browser';
import { apiTokenRequest, interactiveRequest } from '../authConfig';

export interface UserDetails {
    userId: string;
    email: string;
    name: string;
    filesLimit: number;
    matchingLimit: number;
    filesCount: number;
    matchingUsedCount: number;
}

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

// Helper function to construct API URLs
const getApiUrl = (path: string) => {
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    return `${API_BASE_URL}/${cleanPath}`;
};

const getAuthToken = async (instance: IPublicClientApplication, account: AccountInfo): Promise<string> => {
    try {
        // Try to acquire token silently first
        const response = await instance.acquireTokenSilent({
            ...apiTokenRequest,
            account: account
        });
        return response.accessToken;
    } catch (error) {
        if (error instanceof InteractionRequiredAuthError) {
            // If silent token acquisition fails, fall back to interactive method
            const response = await instance.acquireTokenPopup(interactiveRequest);
            return response.accessToken;
        }
        throw error;
    }
};

const getAuthHeaders = async (instance: IPublicClientApplication, account: AccountInfo): Promise<HeadersInit> => {
    const token = await getAuthToken(instance, account);
    return {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    };
};

export const searchUser = async (
    query: string,
    account: AccountInfo,
    instance: IPublicClientApplication
): Promise<UserDetails[]> => {
    try {
        const headers = await getAuthHeaders(instance, account);
        const response = await fetch(getApiUrl(`users/search?q=${encodeURIComponent(query)}`), {
            method: 'GET',
            headers,
            credentials: 'include'
        });

        if (!response.ok) {
            console.error('Failed to find user:', {
                status: response.status,
                statusText: response.statusText,
                headers: Object.fromEntries(response.headers.entries()),
                body: await response.text()
            });
            throw new Error('Failed to find user');
        }

        return await response.json();
    } catch (error) {
        console.error('Error searching for user:', error);
        throw error;
    }
};

export const updateUserLimits = async (
    userId: string,
    filesLimit: number,
    matchingLimit: number,
    account: AccountInfo,
    instance: IPublicClientApplication
): Promise<UserDetails> => {
    try {
        const headers = await getAuthHeaders(instance, account);
        const response = await fetch(getApiUrl('users/limits'), {
            method: 'PUT',
            headers,
            credentials: 'include',
            body: JSON.stringify({
                userId,
                filesLimit,
                matchingLimit
            })
        });

        if (!response.ok) {
            console.error('Failed to update limits:', {
                status: response.status,
                statusText: response.statusText,
                headers: Object.fromEntries(response.headers.entries()),
                body: await response.text()
            });
            throw new Error('Failed to update limits');
        }

        return await response.json();
    } catch (error) {
        console.error('Error updating user limits:', error);
        throw error;
    }
}; 