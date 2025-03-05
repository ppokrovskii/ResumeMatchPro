import { UploadOutlined } from '@ant-design/icons';
import { Button } from 'antd';
import React from 'react';
import styles from './UploadMessage.module.css';

interface UploadMessageProps {
    onUploadClick: () => void;
}

const UploadMessage: React.FC<UploadMessageProps> = ({ onUploadClick }) => {
    return (
        <div className={styles.uploadMessage}>
            <span>Upload or Drag and Drop a CV or Job Description anywhere on the screen</span>
            <Button
                type="primary"
                icon={<UploadOutlined />}
                onClick={onUploadClick}
            >
                Upload
            </Button>
        </div>
    );
};

export default UploadMessage; 