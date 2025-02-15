// services/fileService.ts
import { AccountInfo, IPublicClientApplication } from '@azure/msal-browser';
import { tokenService } from './tokenService';

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

// Helper function to get auth headers using cached token
const getAuthHeadersWithCache = async (instance: IPublicClientApplication, account: AccountInfo): Promise<HeadersInit> => {
    return tokenService.getAuthHeaders(instance, account);
};

export const fetchFiles = async (userId: string, account: AccountInfo, instance: IPublicClientApplication): Promise<RmpFile[]> => {
    try {
        const headers = await getAuthHeadersWithCache(instance, account);
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
        const headers = await getAuthHeadersWithCache(instance, account);
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
    formData.append('type', fileType);
    files.forEach(file => {
        formData.append('content', file);
    });

    // For file uploads, let the browser set the content-type with boundary
    const headers = await getAuthHeadersWithCache(instance, account) as Record<string, string>;
    delete headers['Content-Type'];

    const response = await fetch(getApiUrl('files/upload'), {
        method: 'POST',
        headers,
        credentials: 'include',
        body: formData,
    });

    if (!response.ok) {
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
    const headers = await getAuthHeadersWithCache(instance, account);
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