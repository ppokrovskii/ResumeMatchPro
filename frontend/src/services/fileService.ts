// services/fileService.ts
import { AccountInfo, IPublicClientApplication } from '@azure/msal-browser';
import { tokenService } from './tokenService';

export interface PersonalDetail {
    type: string;
    text: string;
}

export interface ExperienceEntry {
    title: string;
    start_date: string;
    end_date: string;
    lines: string[];
}

export interface EducationEntry {
    institution?: string;
    degree?: string;
    field?: string;
    start_date?: string;
    end_date?: string;
    description?: string;
}

export interface ResumeStructure {
    personal_details: PersonalDetail[];
    professional_summary: string;
    skills: string[];
    experience: ExperienceEntry[];
    education: EducationEntry[];
    additional_information: string[];
}

export interface RmpFile {
    id: string;
    filename: string;
    type: string;
    user_id: string;
    url: string;
    structure?: ResumeStructure;
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

export const fetchFiles = async (account: AccountInfo, instance: IPublicClientApplication): Promise<RmpFile[]> => {
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
    fileId: string,
    fileType: string,
    account: AccountInfo,
    instance: IPublicClientApplication
): Promise<Result[]> => {
    const headers = await getAuthHeadersWithCache(instance, account);
    const response = await fetch(
        getApiUrl(`results?file_id=${fileId}&file_type=${fileType}`),
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

export const getFile = async (fileId: string, account: AccountInfo, instance: IPublicClientApplication): Promise<RmpFile> => {
    try {
        const headers = await getAuthHeadersWithCache(instance, account);
        const response = await fetch(getApiUrl(`files/${fileId}`), {
            method: 'GET',
            headers,
            credentials: 'include'
        });

        if (!response.ok) {
            console.error('Failed to get file:', {
                status: response.status,
                statusText: response.statusText,
                headers: Object.fromEntries(response.headers.entries()),
                body: await response.text()
            });
            throw new Error('Failed to get file');
        }

        return await response.json();
    } catch (error) {
        console.error('Error getting file:', error);
        throw error;
    }
};

export const downloadFile = async (fileId: string, account: AccountInfo, instance: IPublicClientApplication, filename: string): Promise<void> => {
    try {
        const headers = await getAuthHeadersWithCache(instance, account);
        const response = await fetch(getApiUrl(`files/${fileId}/download`), {
            method: 'GET',
            headers,
            credentials: 'include'
        });

        if (!response.ok) {
            console.error('Failed to download file:', {
                status: response.status,
                statusText: response.statusText,
                headers: Object.fromEntries(response.headers.entries()),
                body: await response.text()
            });
            throw new Error('Failed to download file');
        }

        // Get filename from Content-Disposition header or use provided filename
        const contentDisposition = response.headers.get('Content-Disposition');
        const filenameMatch = contentDisposition?.match(/filename="(.+)"/);
        const downloadFilename = filenameMatch ? filenameMatch[1] : filename;

        // Create blob from response and trigger download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = downloadFilename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('Error downloading file:', error);
        throw error;
    }
};