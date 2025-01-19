import { InboxOutlined } from '@ant-design/icons';
import { Upload, message } from 'antd';
import { RcFile, UploadRequestOption } from 'rc-upload/lib/interface';
import React, { useContext, useRef } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import { uploadFiles } from '../../services/fileService';

interface FilesUploadProps {
    onFilesUploaded: (response: { files: { name: string }[] }) => void;
    fileType: string;
}

const FilesUpload: React.FC<FilesUploadProps> = ({ onFilesUploaded, fileType }) => {
    const { isAuthenticated, user } = useContext(AuthContext);
    const uploadingFiles = useRef<Set<string>>(new Set());

    const handleUpload = async (options: UploadRequestOption) => {
        const { file, onSuccess, onError } = options;
        const rcFile = file as RcFile;

        // Check if this file is already being uploaded
        const fileKey = `${rcFile.name}-${rcFile.size}-${rcFile.lastModified}`;
        if (uploadingFiles.current.has(fileKey)) {
            return;
        }

        try {
            uploadingFiles.current.add(fileKey);
            const response = await uploadFiles([file as File], user?.name || '', fileType);
            onFilesUploaded(response);
            onSuccess?.(response);
            message.success(`${rcFile.name} uploaded successfully`);
        } catch (error) {
            console.error('Error uploading files:', error);
            onError?.(error as Error);
            message.error('Upload failed');
        } finally {
            uploadingFiles.current.delete(fileKey);
        }
    };

    if (!isAuthenticated || !user) {
        return null;
    }

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
