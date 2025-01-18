// services/fileService.ts
import { AccountInfo, IPublicClientApplication, InteractionRequiredAuthError } from '@azure/msal-browser';
import { apiTokenRequest, interactiveRequest } from '../authConfig';

export interface RmpFile {
    id: string;
    filename: string;
    type: string;
    user_id: string;
    url: string;
    text: string;
}

export interface FilesResponse {
    files: RmpFile[];
}

export interface Result {
    id: string;
    user_id: string;
    cv: RmpFile;
    jd: RmpFile;
    overall_match_percentage: number;
}

export interface ResultsResponse {
    results: Result[];
}

const API_BASE_URL = 'https://resumematchpro-dev-function-app.azurewebsites.net/api';

const getAuthToken = async (instance: IPublicClientApplication, account: AccountInfo): Promise<string> => {
    try {
        // Try to acquire token silently first
        const response = await instance.acquireTokenSilent({
            ...apiTokenRequest,
            account: account
        });
        // eslint-disable-next-line no-console
        console.log('Token response:', {
            scopes: response.scopes,
            tenantId: response.tenantId,
            tokenType: response.tokenType,
            expiresOn: response.expiresOn,
            token: response.accessToken.substring(0, 20) + '...'  // Log first 20 chars for debugging
        });
        return response.accessToken;
    } catch (error) {
        if (error instanceof InteractionRequiredAuthError) {
            // If silent token acquisition fails, fall back to interactive method
            const response = await instance.acquireTokenPopup(interactiveRequest);
            // eslint-disable-next-line no-console
            console.log('Interactive token response:', {
                scopes: response.scopes,
                tenantId: response.tenantId,
                tokenType: response.tokenType,
                expiresOn: response.expiresOn,
                token: response.accessToken.substring(0, 20) + '...'  // Log first 20 chars for debugging
            });
            return response.accessToken;
        }
        throw error;
    }
};

const getAuthHeaders = async (instance: IPublicClientApplication, account: AccountInfo): Promise<HeadersInit> => {
    const token = await getAuthToken(instance, account);
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    };
    // eslint-disable-next-line no-console
    console.log('Request headers:', {
        ...headers,
        'Authorization': headers.Authorization.substring(0, 27) + '...'  // Log "Bearer " + first 20 chars
    });
    return headers;
};

/**
 * Fetches files based on the user ID.
 * @param userId The user ID for whom to fetch files.
 * @param account The MSAL account info for authentication
 * @param instance The MSAL instance
 */
export const fetchFiles = async (userId: string, account: AccountInfo, instance: IPublicClientApplication): Promise<RmpFile[]> => {
    try {
        const headers = await getAuthHeaders(instance, account);
        // eslint-disable-next-line no-console
        console.log('Fetching files with headers:', headers);

        const response = await fetch(`${API_BASE_URL}/files?user_id=${userId}`, {
            method: 'GET',
            headers,
            credentials: 'include'
        });

        if (!response.ok) {
            // eslint-disable-next-line no-console
            console.error('Failed to fetch files:', {
                status: response.status,
                statusText: response.statusText,
                headers: Object.fromEntries(response.headers.entries()),
                body: await response.text()
            });
            throw new Error(`Network response was not ok: ${response.status}`);
        }

        const data: FilesResponse = await response.json();
        return data.files;
    } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Error fetching files:', error);
        throw error;
    }
};

/**
 * Deletes a file based on its ID.
 * @param fileId The ID of the file to delete.
 * @param account The MSAL account info for authentication
 * @param instance The MSAL instance
 */
export const deleteFile = async (fileId: string, account: AccountInfo, instance: IPublicClientApplication): Promise<void> => {
    const headers = await getAuthHeaders(instance, account);
    const response = await fetch(`${API_BASE_URL}/files/${fileId}`, {
        method: 'DELETE',
        headers,
        credentials: 'include'
    });

    if (!response.ok) {
        throw new Error('Failed to delete file');
    }
};

interface FileUploadResponse {
    files: File[];
    message?: string;
}

export const uploadFiles = async (
    files: File[],
    userId: string,
    fileType: string,
    account: AccountInfo,
    instance: IPublicClientApplication
): Promise<FileUploadResponse> => {
    const formData = new FormData();
    files.forEach(file => formData.append('content', file));
    formData.append('user_id', userId);
    formData.append('type', fileType);

    const headers = await getAuthHeaders(instance, account) as Record<string, string>;
    // Remove content-type for FormData
    delete headers['Content-Type'];

    const response = await fetch(`${API_BASE_URL}/files/upload`, {
        method: 'POST',
        headers,
        credentials: 'include',
        body: formData,
    });

    if (!response.ok) {
        // eslint-disable-next-line no-console
        console.error('Upload failed:', {
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers.entries()),
            body: await response.text()
        });
        throw new Error('Upload failed');
    }

    return response.json();
};

export const getMatchingResults = async (
    userId: string,
    fileId: string,
    fileType: string,
    account: AccountInfo,
    instance: IPublicClientApplication
): Promise<Result[]> => {
    const headers = await getAuthHeaders(instance, account);
    const response = await fetch(
        `${API_BASE_URL}/results?user_id=${userId}&file_id=${fileId}&file_type=${fileType}`,
        {
            headers,
            credentials: 'include'
        }
    );

    if (!response.ok) {
        // eslint-disable-next-line no-console
        console.error('Failed to fetch matching results:', {
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers.entries()),
            body: await response.text()
        });
        throw new Error('Failed to fetch matching results');
    }

    const data: ResultsResponse = await response.json();
    return data.results;
};