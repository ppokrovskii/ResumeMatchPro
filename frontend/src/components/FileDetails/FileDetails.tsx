import { CloseOutlined, DownloadOutlined } from '@ant-design/icons';
import { useMsal } from '@azure/msal-react';
import { Button, Typography, message } from 'antd';
import React from 'react';
import { RmpFile, downloadFile } from '../../services/fileService';
import styles from './FileDetails.module.css';

const { Title } = Typography;

interface FileDetailsProps {
    file: RmpFile;
    onBack: () => void;
}

const FileDetails: React.FC<FileDetailsProps> = ({ file, onBack }) => {
    const { instance, accounts } = useMsal();

    const handleDownload = async () => {
        try {
            const account = accounts[0];
            if (!account) {
                throw new Error('No account found');
            }
            await downloadFile(file.id, account, instance, file.filename);
        } catch (error) {
            console.error('Error downloading file:', error);
            message.error('Failed to download file');
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.headerLeft}>
                    <Button
                        type="text"
                        icon={<DownloadOutlined />}
                        onClick={handleDownload}
                        className={styles.downloadButton}
                        aria-label="Download file"
                    />
                    <Title level={4} className={styles.filename}>
                        {file.filename}
                    </Title>
                </div>
                <Button
                    type="text"
                    icon={<CloseOutlined />}
                    onClick={onBack}
                    className={styles.closeButton}
                    aria-label="Close file details"
                />
            </div>
            <div className={styles.content}>
                <pre className={styles.fileText}>
                    {file.text}
                </pre>
            </div>
        </div>
    );
};

export default FileDetails; 