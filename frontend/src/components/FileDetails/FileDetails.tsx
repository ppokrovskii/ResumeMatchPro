import { CloseOutlined, DownloadOutlined } from '@ant-design/icons';
import { useMsal } from '@azure/msal-react';
import { Button, Card, List, Spin, Tag, Typography, message } from 'antd';
import React from 'react';
import { RmpFile, downloadFile } from '../../services/fileService';
import styles from './FileDetails.module.css';

const { Title, Paragraph, Text } = Typography;

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
                {/* Always show content */}
                {file && (
                    <div className={styles.content}>
                        {/* Display file type */}
                        {file.type && (
                            <div className={styles.fileType}>
                                <Tag color={file.type === 'CV' ? 'blue' : 'green'}>
                                    {file.type === 'CV' ? 'Resume/CV' : 'Job Description'}
                                </Tag>
                            </div>
                        )}

                        {/* Summary section for JD */}
                        {file.type === 'JD' && file.structure && 'role_summary' in file.structure && (
                            <div className={styles.section}>
                                <Title level={5}>Job Description</Title>
                                <Paragraph>{file.structure.role_summary as string}</Paragraph>
                            </div>
                        )}

                        {/* Personal details section (mainly for CV) */}
                        {renderPersonalDetails()}

                        {/* Job requirements for JD */}
                        {file.type === 'JD' && file.structure &&
                            'required_skills' in file.structure &&
                            Array.isArray(file.structure.required_skills) &&
                            file.structure.required_skills.length > 0 && (
                                <div className={styles.section}>
                                    <Title level={5}>Required Skills</Title>
                                    <List
                                        dataSource={file.structure.required_skills as string[]}
                                        renderItem={(skill: string) => (
                                            <List.Item>
                                                <Text>{skill}</Text>
                                            </List.Item>
                                        )}
                                    />
                                </div>
                            )}

                        {/* Skills section for CV */}
                        {file.type === 'CV' && file.structure &&
                            'skills' in file.structure &&
                            Array.isArray(file.structure.skills) &&
                            file.structure.skills.length > 0 && (
                                <div className={styles.section}>
                                    <Title level={5}>Skills</Title>
                                    <div className={styles.skillsList}>
                                        {(file.structure.skills as string[]).map((skill, index) => (
                                            <Tag key={index} className={styles.skillTag}>{skill}</Tag>
                                        ))}
                                    </div>
                                </div>
                            )}
                    </div>
                )}
            </Spin>
        </Card>
    );
};

export default FileDetails; 