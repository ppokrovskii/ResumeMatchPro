// services/fileService.ts

export interface File {
    id: string;
    filename: string;
    type: string;
    user_id: string;
    url: string;
    text: string;
}

export interface FilesResponse {
    files: File[];
}

const API_BASE_URL = 'http://localhost:7071/api';

/**
 * Fetches files based on the user ID and type.
 * @param userId The user ID for whom to fetch files.
 * @param type The type of files to fetch (e.g., 'JD' for Job Description).
 */
export const fetchFiles = async (userId: string, type?: string): Promise<File[]> => {
    const response = await fetch(`${API_BASE_URL}/files?user_id=${userId}&type=${type || ''}`);
    if (!response.ok) {
        throw new Error('Failed to fetch files');
    }
    const data: FilesResponse = await response.json();
    return data.files;
};

/**
 * Deletes a file based on its ID.
 * @param fileId The ID of the file to delete.
 */
export const deleteFile = async (fileId: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/files/${fileId}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error('Failed to delete file');
    }
};

export const uploadFiles = async (files: FileList, userId: string, type: string): Promise<any> => {
    const formData = new FormData();
    Array.from(files).forEach(file => {
        formData.append('content', file);
    });
    formData.append('user_id', userId);
    formData.append('type', type);

    const response = await fetch(`${API_BASE_URL}/files/upload`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error('File upload failed');
    }

    const data = await response.json();
    return data.files;
};

export interface Result {
    id: string;
    user_id: string;
    cv: File;
    jd: File;
    jd_requirements: {
        skills: string[];
        experience: string[];
        education: string[];
    };
    candidate_capabilities: {
        skills: string[];
        experience: string[];
        education: string[];
    };
    cv_match: {
        skills_match: string[];
        experience_match: string[];
        education_match: string[];
        gaps: string[];
    };
    overall_match_percentage: number;
}

export interface ResultsResponse {
    results: Result[];
}

export const getMatchingResults = async (userId: string, fileId: string, fileType: string): Promise<Result[]> => {
    const response = await fetch(`${API_BASE_URL}/results?user_id=${userId}&file_id=${fileId}&file_type=${fileType}`);
    if (!response.ok) {
        throw new Error('Failed to fetch matching results');
    }
    const data: ResultsResponse = await response.json();
    return data.results;
};