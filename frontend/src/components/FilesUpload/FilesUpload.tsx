import { InboxOutlined } from '@ant-design/icons';
import { useMsal } from '@azure/msal-react';
import { Upload } from 'antd';
import { RcFile, UploadRequestOption } from 'rc-upload/lib/interface';
import React, { useRef } from 'react';
import { uploadFiles } from '../../services/fileService';

interface FilesUploadProps {
    onFilesUploaded: (files: File[], fileType: string) => void;
    fileType: string;
}

const FilesUpload: React.FC<FilesUploadProps> = ({ onFilesUploaded, fileType }) => {
    const { instance, accounts } = useMsal();
    const account = accounts[0];
    const claims = account?.idTokenClaims as { sub?: string };
    const userId = claims?.sub || '1'; // Fallback to '1' for development
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
            const response = await uploadFiles([file as File], userId, fileType, account, instance);
            if (response.files) {
                onFilesUploaded(response.files, fileType);
                onSuccess?.(response);
            } else {
                throw new Error('No files returned from server');
            }
        } catch (error) {
            console.error('Error uploading files:', error);
            onError?.(error as Error);
        } finally {
            uploadingFiles.current.delete(fileKey);
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
