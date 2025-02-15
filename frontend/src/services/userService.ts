import { AccountInfo, IPublicClientApplication } from '@azure/msal-browser';
import { tokenService } from './tokenService';

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

export const searchUser = async (
    query: string,
    account: AccountInfo,
    instance: IPublicClientApplication
): Promise<UserDetails[]> => {
    try {
        const headers = await tokenService.getAuthHeaders(instance, account);
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
        const headers = await tokenService.getAuthHeaders(instance, account);
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

export const getCurrentUser = async (
    account: AccountInfo,
    instance: IPublicClientApplication
): Promise<UserDetails> => {
    try {
        const headers = await tokenService.getAuthHeaders(instance, account);
        const response = await fetch(getApiUrl('users/me'), {
            method: 'GET',
            headers,
            credentials: 'include'
        });

        if (!response.ok) {
            console.error('Failed to get current user:', {
                status: response.status,
                statusText: response.statusText,
                headers: Object.fromEntries(response.headers.entries()),
                body: await response.text()
            });
            throw new Error('Failed to get current user');
        }

        return await response.json();
    } catch (error) {
        console.error('Error getting current user:', error);
        throw error;
    }
}; 