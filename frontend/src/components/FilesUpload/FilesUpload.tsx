import React from 'react';
import { Upload } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { uploadFiles } from '../../services/fileService';

interface FilesUploadProps {
    onFilesUploaded: (files: File[], fileType: string) => void;
    fileType: string;
}

const FilesUpload: React.FC<FilesUploadProps> = ({ onFilesUploaded, fileType }) => {
    const userId = '1'; // Normally taken from global state or props

    const handleUpload = async (options: any) => {
        const { file, onSuccess, onError } = options;
        try {
            const response = await uploadFiles([file], userId, fileType);
            if (response.files) {
                onFilesUploaded(response.files, fileType);
                onSuccess(response, file);
            } else {
                throw new Error('No files returned from server');
            }
        } catch (error) {
            console.error('Error uploading files:', error);
            onError(error);
        }
    };

    return (
        <Upload.Dragger
            multiple
            accept=".pdf,.docx"
            customRequest={handleUpload}
            className="drop-area"
        >
            <p className="ant-upload-drag-icon">
                <InboxOutlined />
            </p>
            <p className="ant-upload-text">Click or drag file to this area to upload</p>
        </Upload.Dragger>
    );
};

export default FilesUpload;
