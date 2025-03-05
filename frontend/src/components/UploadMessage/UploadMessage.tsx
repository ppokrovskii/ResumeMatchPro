import { CloudUploadOutlined, FileTextOutlined } from '@ant-design/icons';
import { Button } from 'antd';
import React, { useRef } from 'react';
import styles from './UploadMessage.module.css';

interface UploadMessageProps {
    onUploadClick: () => void;
    onFilesSelected?: (files: FileList) => void;
}

const UploadMessage: React.FC<UploadMessageProps> = ({ onUploadClick, onFilesSelected }) => {
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleButtonClick = () => {
        if (onFilesSelected) {
            // If onFilesSelected is provided, directly open file selector
            fileInputRef.current?.click();
        } else {
            // Fall back to the original behavior if onFilesSelected is not provided
            onUploadClick();
        }
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files.length > 0 && onFilesSelected) {
            onFilesSelected(event.target.files);
            // Reset the file input value after selection
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    return (
        <div className={styles.uploadMessage}>
            <div className={styles.messageContent}>
                <FileTextOutlined className={styles.fileIcon} />
                <span>Upload or Drag and Drop a CV or Job Description anywhere on the screen</span>
            </div>
            <Button
                type="primary"
                icon={<CloudUploadOutlined />}
                onClick={handleButtonClick}
                size="large"
                className={styles.uploadButton}
            >
                Upload Files
            </Button>
            {onFilesSelected && (
                <input
                    type="file"
                    ref={fileInputRef}
                    className={styles.hiddenFileInput}
                    onChange={handleFileChange}
                    accept=".pdf,.doc,.docx"
                    multiple
                />
            )}
        </div>
    );
};

export default UploadMessage; 