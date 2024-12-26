// services/fileService.ts

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


const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:7071/api';

/**
 * Fetches files based on the user ID and type.
 * @param userId The user ID for whom to fetch files.
 * @param type The type of files to fetch (e.g., 'JD' for Job Description).
 */
export const fetchFiles = async (userId: string): Promise<RmpFile[]> => {
    try {
        const response = await fetch(`${API_BASE_URL}/files/${userId}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching files:', error);
        return []; // Return empty array on error instead of throwing
    }
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

interface FileUploadResponse {
    files: File[];
    message?: string;
}

interface MatchingResult {
    score: number;
    matches: string[];
    suggestions: string[];
}

export const uploadFiles = async (files: File[], userId: string, fileType: string): Promise<FileUploadResponse> => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('userId', userId);
    formData.append('fileType', fileType);

    const response = await fetch(`${process.env.REACT_APP_API_URL}/files/upload`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error('Upload failed');
    }

    return response.json();
};




export interface Result {
    id: string;
    user_id: string;
    cv: RmpFile;
    jd: RmpFile;
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

export const getMatchingResults = async (userId: string, fileId: string, fileType: string): Promise<MatchingResult[]> => {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/results/${userId}/${fileId}?type=${fileType}`);
    
    if (!response.ok) {
        throw new Error('Failed to fetch matching results');
    }

    return response.json();
};