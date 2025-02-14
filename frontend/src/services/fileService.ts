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
        'X-Requested-With': 'XMLHttpRequest'
    };
};

export const fetchFiles = async (userId: string, account: AccountInfo, instance: IPublicClientApplication): Promise<RmpFile[]> => {
    try {
        const headers = await getAuthHeaders(instance, account);
        const response = await fetch(getApiUrl('files'), {
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

export const deleteFile = async (fileId: string, account: AccountInfo, instance: IPublicClientApplication): Promise<void> => {
    try {
        const headers = await getAuthHeaders(instance, account);
        const response = await fetch(getApiUrl(`files/${fileId}`), {
            method: 'DELETE',
            headers,
            credentials: 'include'
        });

        if (!response.ok) {
            // eslint-disable-next-line no-console
            console.error('Failed to delete file:', {
                status: response.status,
                statusText: response.statusText,
                headers: Object.fromEntries(response.headers.entries()),
                body: await response.text()
            });
            throw new Error('Failed to delete file');
        }
    } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Error deleting file:', error);
        throw error;
    }
};

interface FileUploadResponse {
    files: { name: string }[];
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

    // Add text fields first
    // formData.append('user_id', userId);
    formData.append('type', fileType);

    // Add file with explicit filename
    files.forEach(file => {
        // Ensure we're sending the file with the correct field name and filename
        formData.append('content', file);
    });

    const headers = await getAuthHeaders(instance, account);
    const response = await fetch(getApiUrl('files/upload'), {
        method: 'POST',
        headers: {
            ...headers,
        } as HeadersInit,
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
        getApiUrl(`results?user_id=${userId}&file_id=${fileId}&file_type=${fileType}`),
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