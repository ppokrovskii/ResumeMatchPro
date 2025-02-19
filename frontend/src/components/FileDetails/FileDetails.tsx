import { ArrowLeftOutlined } from '@ant-design/icons';
import { Button, Typography } from 'antd';
import React from 'react';
import { RmpFile } from '../../services/fileService';
import styles from './FileDetails.module.css';

const { Title } = Typography;

interface FileDetailsProps {
    file: RmpFile;
    onBack: () => void;
}

const FileDetails: React.FC<FileDetailsProps> = ({ file, onBack }) => {
    return (
        <div className={styles.container}>
            <Button
                type="link"
                icon={<ArrowLeftOutlined />}
                onClick={onBack}
                className={styles.backButton}
            >
                Back to list
            </Button>

            <div className={styles.header}>
                <Title level={4} className={styles.filename}>
                    {file.filename}
                </Title>
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