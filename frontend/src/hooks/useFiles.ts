import { AccountInfo, InteractionRequiredAuthError, IPublicClientApplication } from '@azure/msal-browser';
import { useCallback, useEffect, useState } from 'react';
import { fetchFiles, RmpFile } from '../services/fileService';

interface IdTokenClaims {
    sub: string;
    [key: string]: unknown;
}

export const useFiles = (
    instance: IPublicClientApplication,
    accounts: AccountInfo[],
    isAuthenticated: boolean
) => {
    const [cvFiles, setCvFiles] = useState<RmpFile[]>([]);
    const [jdFiles, setJdFiles] = useState<RmpFile[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const refreshFiles = useCallback(async () => {
        if (!isAuthenticated || accounts.length === 0) return;

        try {
            setIsLoading(true);
            const account = accounts[0];
            const response = await instance.acquireTokenSilent({
                scopes: ['openid'],
                account: account
            });
            const claims = response.idTokenClaims as IdTokenClaims;
            const userId = claims.sub;
            if (!userId) {
                throw new Error('No user ID found in token claims');
            }

            const loadedFiles = await fetchFiles(userId, account, instance);
            setCvFiles(loadedFiles.filter((file: RmpFile) => file.type === 'CV'));
            setJdFiles(loadedFiles.filter((file: RmpFile) => file.type === 'JD'));
        } catch (error) {
            if (error instanceof InteractionRequiredAuthError) {
                // Handle interaction required error if needed
                console.error('Interaction required:', error);
            } else {
                console.error('Error loading files:', error);
            }
        } finally {
            setIsLoading(false);
        }
    }, [instance, accounts, isAuthenticated]);

    // Initial load
    useEffect(() => {
        refreshFiles();
    }, [refreshFiles]);

    return {
        cvFiles,
        jdFiles,
        isLoading,
        refreshFiles
    };
}; 