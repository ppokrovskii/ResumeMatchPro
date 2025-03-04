import { useMsal } from '@azure/msal-react';
import { message } from 'antd';
import React, { useCallback, useContext, useEffect, useRef, useState } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import { uploadFiles } from '../../services/fileService';
import './GlobalDragDrop.css';

interface GlobalDragDropProps {
    onFilesUploaded: (response: { files: { name: string }[] }, fileType: 'CV' | 'JD') => void;
    defaultFileType?: 'CV' | 'JD';
    children: React.ReactNode;
}

const GlobalDragDrop: React.FC<GlobalDragDropProps> = ({
    onFilesUploaded,
    defaultFileType = 'CV',
    children
}) => {
    const [isDragging, setIsDragging] = useState(false);
    const { isAuthenticated, user } = useContext(AuthContext);
    const { instance, accounts } = useMsal();
    const dragCounter = useRef(0);

    // Event handlers using useCallback to properly memoize them for the dependency array
    const handleDragEnter = useCallback((e: DragEvent) => {
        e.preventDefault();
        e.stopPropagation();

        dragCounter.current += 1;

        if (e.dataTransfer?.items && e.dataTransfer.items.length > 0) {
            setIsDragging(true);
        }
    }, []);

    const handleDragOver = useCallback((e: DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (!isDragging) {
            setIsDragging(true);
        }
    }, [isDragging]);

    const handleDragLeave = useCallback((e: DragEvent) => {
        e.preventDefault();
        e.stopPropagation();

        dragCounter.current -= 1;

        if (dragCounter.current === 0) {
            setIsDragging(false);
        }
    }, []);

    const handleDrop = useCallback(async (e: DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        dragCounter.current = 0;

        if (!isAuthenticated || !user) {
            message.error('You must be logged in to upload files');
            return;
        }

        if (!e.dataTransfer?.files || e.dataTransfer.files.length === 0) {
            return;
        }

        const files = Array.from(e.dataTransfer.files);
        const validExtensions = ['.pdf', '.docx', '.doc'];
        const validFiles = files.filter(file => {
            const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
            return validExtensions.includes(ext);
        });

        if (validFiles.length === 0) {
            message.error('Only PDF and Word documents are allowed');
            return;
        }

        try {
            const account = accounts[0];
            if (!account) {
                throw new Error('No account found');
            }

            // Show file type selection if multiple files are dropped
            if (validFiles.length > 1) {
                const userFileType = window.confirm(
                    'Please select the file type:\n\nClick OK for CVs, Cancel for Job Descriptions'
                ) ? 'CV' : 'JD';

                const response = await uploadFiles(validFiles, userFileType, account, instance);
                onFilesUploaded(response, userFileType);
                message.success(`${validFiles.length} files uploaded successfully as ${userFileType}`);
            } else {
                // For single file, use modal dialog to select type
                const userFileType = window.confirm(
                    'Please select the file type:\n\nClick OK for CV, Cancel for Job Description'
                ) ? 'CV' : 'JD';

                const response = await uploadFiles(validFiles, userFileType, account, instance);
                onFilesUploaded(response, userFileType);
                message.success(`${validFiles[0].name} uploaded successfully as ${userFileType}`);
            }
        } catch (error) {
            console.error('Error uploading files:', error);
            const errorMessage = error instanceof Error ? error.message : 'Upload failed';
            message.error(errorMessage);
        }
    }, [isAuthenticated, user, accounts, instance, onFilesUploaded]);

    // Set up event listeners for the entire document
    useEffect(() => {
        if (!isAuthenticated) return;

        document.addEventListener('dragenter', handleDragEnter);
        document.addEventListener('dragover', handleDragOver);
        document.addEventListener('dragleave', handleDragLeave);
        document.addEventListener('drop', handleDrop);

        return () => {
            document.removeEventListener('dragenter', handleDragEnter);
            document.removeEventListener('dragover', handleDragOver);
            document.removeEventListener('dragleave', handleDragLeave);
            document.removeEventListener('drop', handleDrop);
        };
    }, [isAuthenticated, handleDragEnter, handleDragOver, handleDragLeave, handleDrop]);

    return (
        <div className="global-drag-drop-container">
            {children}
            {isDragging && (
                <div className="global-drag-overlay">
                    <div className="global-drag-message">
                        <div className="global-drag-icon">📄</div>
                        <h2>Drop files anywhere to upload</h2>
                        <p>PDF and Word documents will be processed automatically</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default GlobalDragDrop; 