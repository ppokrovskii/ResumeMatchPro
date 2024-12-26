import React from 'react';
import { Upload } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { uploadFiles } from '../../services/fileService';
import { UploadRequestOption } from 'rc-upload/lib/interface';

interface FilesUploadProps {
    onFilesUploaded: (files: File[], fileType: string) => void;
    fileType: string;
}

const FilesUpload: React.FC<FilesUploadProps> = ({ onFilesUploaded, fileType }) => {
    const userId = '1'; // Normally taken from global state or props

    const handleUpload = async (options: UploadRequestOption) => {
        const { file, onSuccess, onError } = options;
        try {
            const response = await uploadFiles([file as File], userId, fileType);
            if (response.files) {
                onFilesUploaded(response.files, fileType);
                onSuccess?.(response, file);
            } else {
                throw new Error('No files returned from server');
            }
        } catch (error) {
            console.error('Error uploading files:', error);
            onError?.(error as Error);
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
