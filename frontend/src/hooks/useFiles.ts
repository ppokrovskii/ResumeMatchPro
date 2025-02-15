import { AccountInfo, IPublicClientApplication } from '@azure/msal-browser';
import { useCallback, useEffect, useRef, useState } from 'react';
import { fetchFiles, RmpFile } from '../services/fileService';

export const useFiles = (
    instance: IPublicClientApplication,
    accounts: AccountInfo[],
    isAuthenticated: boolean
) => {
    const [cvFiles, setCvFiles] = useState<RmpFile[]>([]);
    const [jdFiles, setJdFiles] = useState<RmpFile[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const isLoadingRef = useRef(false);

    const refreshFiles = useCallback(async () => {
        if (!isAuthenticated || accounts.length === 0 || isLoadingRef.current) return;

        try {
            isLoadingRef.current = true;
            setIsLoading(true);
            const account = accounts[0];

            const loadedFiles = await fetchFiles(account, instance);
            setCvFiles(loadedFiles.filter((file: RmpFile) => file.type === 'CV'));
            setJdFiles(loadedFiles.filter((file: RmpFile) => file.type === 'JD'));
        } catch (error) {
            console.error('Error loading files:', error);
        } finally {
            setIsLoading(false);
            isLoadingRef.current = false;
        }
    }, [instance, accounts, isAuthenticated]);

    // Initial load and refresh when auth state changes
    useEffect(() => {
        if (isAuthenticated && accounts.length > 0) {
            refreshFiles();
        }
    }, [isAuthenticated, accounts.length, refreshFiles]); // Include refreshFiles in dependencies

    return {
        cvFiles,
        jdFiles,
        isLoading,
        refreshFiles
    };
}; 