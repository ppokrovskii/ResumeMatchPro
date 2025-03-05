import { CloseOutlined, DownloadOutlined } from '@ant-design/icons';
import { useMsal } from '@azure/msal-react';
import { Button, Card, List, Spin, Tag, Typography, message } from 'antd';
import React from 'react';
import { RmpFile, downloadFile } from '../../services/fileService';
import styles from './FileDetails.module.css';

const { Title, Text, Paragraph } = Typography;

interface FileDetailsProps {
    file: RmpFile | null;
    isLoading?: boolean;
    onClose: () => void;
    canRunMatching?: boolean;
    onRunMatching?: () => Promise<void>;
}

const FileDetails: React.FC<FileDetailsProps> = ({
    file,
    isLoading = false,
    onClose,
    canRunMatching = false
}) => {
    const { instance, accounts } = useMsal();

    const handleDownload = async () => {
        try {
            if (!file) return;

            const account = accounts[0];
            if (!account) {
                throw new Error('No account found');
            }
            await downloadFile(file.id, account, instance, file.filename);
        } catch (error) {
            // eslint-disable-next-line no-console
            console.error('Error downloading file:', error);
            message.error('Failed to download file');
        }
    };

    const getStatusTag = (file: RmpFile) => {
        if (!file.status) return null;

        let color = 'default';
        let text = file.status;

        switch (file.status) {
            case 'UPLOADED':
                color = 'blue';
                text = 'Uploaded';
                break;
            case 'PROCESSING':
                color = 'processing';
                text = 'Processing';
                break;
            case 'EXTRACTING_TEXT':
                color = 'processing';
                text = 'Extracting Text';
                break;
            case 'ANALYZING':
                color = 'processing';
                text = 'Analyzing';
                break;
            case 'COMPLETED':
                color = 'success';
                text = 'Completed';
                break;
            case 'ERROR':
                color = 'error';
                text = 'Error';
                break;
            default:
                color = 'default';
        }

        return (
            <Tag color={color} className={styles.statusTag}>{text}</Tag>
        );
    };

    const renderPersonalDetails = () => {
        if (!file?.structure?.personal_details?.length) return null;
        return (
            <div className={styles.section}>
                <Title level={5}>Personal Details</Title>
                <List
                    dataSource={file.structure.personal_details}
                    renderItem={detail => (
                        <List.Item>
                            <Text strong>{detail.type}: </Text>
                            <Text>{detail.text}</Text>
                        </List.Item>
                    )}
                />
            </div>
        );
    };

    if (isLoading) {
        return (
            <div className={styles.container}>
                <div className={styles.loadingContainer}>
                    <Spin size="large" />
                    <Text>Loading file details...</Text>
                </div>
            </div>
        );
    }

    if (!file) {
        return (
            <div className={styles.container}>
                <div className={styles.header}>
                    <Button
                        type="text"
                        icon={<CloseOutlined />}
                        onClick={onClose}
                        className={styles.closeButton}
                        aria-label="Close file details"
                    />
                </div>
                <div className={styles.content}>
                    <Text>No file selected.</Text>
                </div>
            </div>
        );
    }

    return (
        <Card
            className={styles.fileDetails}
            title={
                <div className={styles.cardHeader}>
                    <div className={styles.titleContainer}>
                        <Title level={4} className={styles.title}>
                            {file?.filename}
                        </Title>
                        {file && getStatusTag(file)}
                    </div>
                    <Button
                        type="text"
                        icon={<CloseOutlined />}
                        onClick={onClose}
                        className={styles.closeButton}
                    />
                </div>
            }
            extra={
                <Button
                    type="primary"
                    icon={<DownloadOutlined />}
                    onClick={handleDownload}
                    disabled={!file}
                >
                    Download
                </Button>
            }
        >
            <Spin spinning={isLoading}>
                {file && file.status === 'PROCESSING' && (
                    <div className={styles.processingMessage}>
                        <Spin size="small" />
                        <Text type="secondary">{file.status_message || 'File is being processed...'}</Text>
                    </div>
                )}

                {file && file.status === 'ERROR' && (
                    <div className={styles.errorMessage}>
                        <Text type="danger">{file.status_message || 'An error occurred during processing'}</Text>
                    </div>
                )}

                {/* Only show content if file is completed or no status is available (backward compatibility) */}
                {file && (!file.status || file.status === 'COMPLETED') && (
                    <>
                        {file.type && (
                            <div className={styles.fileType}>
                                <Tag color={file.type === 'CV' ? 'blue' : 'green'}>
                                    {file.type === 'CV' ? 'Resume/CV' : 'Job Description'}
                                </Tag>
                            </div>
                        )}

                        {/* Render file structure if available */}
                        {file.structure && (
                            <div className={styles.fileContent}>
                                {renderPersonalDetails()}

                                {file.structure.professional_summary && (
                                    <div className={styles.section}>
                                        <Title level={5}>Professional Summary</Title>
                                        <Paragraph>{file.structure.professional_summary}</Paragraph>
                                    </div>
                                )}

                                {/* Rest of the component remains unchanged */}
                            </div>
                        )}
                    </>
                )}
            </Spin>
        </Card>
    );
};

export default FileDetails; 