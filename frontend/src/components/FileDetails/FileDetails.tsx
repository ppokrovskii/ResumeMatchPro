import { CloseOutlined, DownloadOutlined } from '@ant-design/icons';
import { useMsal } from '@azure/msal-react';
import { Button, Card, Divider, List, Tag, Typography, message } from 'antd';
import React from 'react';
import { RmpFile, downloadFile } from '../../services/fileService';
import styles from './FileDetails.module.css';

const { Title, Text, Paragraph } = Typography;

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

    const renderPersonalDetails = () => {
        if (!file.structure?.personal_details?.length) return null;
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

    const renderSkills = () => {
        if (!file.structure?.skills?.length) return null;
        return (
            <div className={styles.section}>
                <Title level={5}>Skills</Title>
                <div className={styles.skills}>
                    {file.structure.skills.map((skill, index) => (
                        <Tag key={index} color="blue">{skill}</Tag>
                    ))}
                </div>
            </div>
        );
    };

    const renderExperience = () => {
        if (!file.structure?.experience?.length) return null;
        return (
            <div className={styles.section}>
                <Title level={5}>Experience</Title>
                {file.structure.experience.map((exp, index) => (
                    <Card key={index} className={styles.experienceCard}>
                        <Title level={5}>{exp.title}</Title>
                        <Text type="secondary">{exp.start_date} - {exp.end_date}</Text>
                        <List
                            dataSource={exp.lines}
                            renderItem={line => (
                                <List.Item>
                                    <Text>{line}</Text>
                                </List.Item>
                            )}
                        />
                    </Card>
                ))}
            </div>
        );
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
                {file.structure ? (
                    <>
                        {renderPersonalDetails()}
                        <Divider />
                        <div className={styles.section}>
                            <Title level={5}>Professional Summary</Title>
                            <Paragraph>{file.structure.professional_summary}</Paragraph>
                        </div>
                        <Divider />
                        {renderSkills()}
                        <Divider />
                        {renderExperience()}
                        {file.structure.additional_information?.length > 0 && (
                            <>
                                <Divider />
                                <div className={styles.section}>
                                    <Title level={5}>Additional Information</Title>
                                    <List
                                        dataSource={file.structure.additional_information}
                                        renderItem={info => (
                                            <List.Item>
                                                <Text>{info}</Text>
                                            </List.Item>
                                        )}
                                    />
                                </div>
                            </>
                        )}
                    </>
                ) : (
                    <Text>No structured information available for this file.</Text>
                )}
            </div>
        </div>
    );
};

export default FileDetails; 