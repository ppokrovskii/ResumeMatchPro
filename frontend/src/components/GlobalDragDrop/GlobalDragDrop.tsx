import { useMsal } from '@azure/msal-react';
import { message } from 'antd';
import { RcFile } from 'rc-upload/lib/interface';
import React, { useCallback, useContext, useRef, useState } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import { uploadFiles } from '../../services/fileService';
import styles from './GlobalDragDrop.module.css';

interface GlobalDragDropProps {
    onFilesUploaded: (response: { files: { name: string }[] }) => void;
    children: React.ReactNode;
}

const GlobalDragDrop: React.FC<GlobalDragDropProps> = ({
    onFilesUploaded,
    children
}) => {
    const { isAuthenticated } = useContext(AuthContext);
    const { instance, accounts } = useMsal();
    const account = accounts[0];

    const [isDragging, setIsDragging] = useState(false);
    const dragCounter = useRef(0);

    const handleDragEnter = useCallback((e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        dragCounter.current += 1;
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        dragCounter.current -= 1;

        if (dragCounter.current === 0) {
            setIsDragging(false);
        }
    }, []);

    const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.dataTransfer) {
            e.dataTransfer.dropEffect = 'copy';
        }
    }, []);

    const handleDrop = useCallback(async (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        dragCounter.current = 0;

        if (!isAuthenticated) {
            message.error('Please sign in to upload files');
            return;
        }

        const { files } = e.dataTransfer;
        if (files && files.length > 0) {
            const validFiles: RcFile[] = [];
            for (let i = 0; i < files.length; i++) {
                const file = files[i] as RcFile;
                if (file.size / 1024 / 1024 < 10) { // Limit to 10MB
                    validFiles.push(file);
                } else {
                    message.error(`${file.name} is too large, please upload files smaller than 10MB.`);
                }
            }

            if (validFiles.length === 0) {
                return;
            }

            try {
                message.loading('Uploading files...', 0);
                const response = await uploadFiles(validFiles, account, instance);
                message.destroy();
                message.success(`${validFiles.length} file(s) uploaded successfully`);
                onFilesUploaded(response);
            } catch (error) {
                message.destroy();
                message.error('Upload failed: ' + (error instanceof Error ? error.message : String(error)));
            }
        }
    }, [isAuthenticated, onFilesUploaded, account, instance]);

    return (
        <div
            className={`${styles.globalDragDrop} ${isDragging ? styles.dragging : ''}`}
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
        >
            {isDragging && (
                <div className={styles.dragOverlay}>
                    <div className={styles.dropMessage}>
                        <div className={styles.dropIcon}>
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 2L8 6H11V15H13V6H16L12 2Z" fill="currentColor" />
                                <path d="M19 9H15V11H19V19H5V11H9V9H5C3.89543 9 3 9.89543 3 11V19C3 20.1046 3.89543 21 5 21H19C20.1046 21 21 20.1046 21 19V11C21 9.89543 20.1046 9 19 9Z" fill="currentColor" />
                            </svg>
                        </div>
                        <div className={styles.dropText}>Drop files to upload</div>
                    </div>
                </div>
            )}
            {children}
        </div>
    );
};

export default GlobalDragDrop; 