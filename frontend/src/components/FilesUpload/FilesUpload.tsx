import { InboxOutlined } from '@ant-design/icons';
import { useMsal } from '@azure/msal-react';
import { Upload, message } from 'antd';
import { RcFile, UploadRequestOption } from 'rc-upload/lib/interface';
import React, { useContext, useRef, useState } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import { uploadFiles } from '../../services/fileService';

interface FilesUploadProps {
    onFilesUploaded: (response: { files: { name: string }[] }) => void;
    fileType: string;
}

const FilesUpload: React.FC<FilesUploadProps> = ({ onFilesUploaded, fileType }) => {
    const { isAuthenticated, user } = useContext(AuthContext);
    const { instance, accounts } = useMsal();
    const uploadingFiles = useRef<Set<string>>(new Set());
    const [fileList, setFileList] = useState<RcFile[]>([]);

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
            const account = accounts[0];
            if (!account) {
                throw new Error('No account found');
            }

            const response = await uploadFiles([rcFile], fileType, account, instance);
            onFilesUploaded(response);
            onSuccess?.(response);
            message.success(`${rcFile.name} uploaded successfully`);
            // Clear the file list after successful upload
            setFileList([]);
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
            fileList={fileList}
            onChange={({ fileList }) => setFileList(fileList as RcFile[])}
        >
            <p className="ant-upload-drag-icon">
                <InboxOutlined />
            </p>
            <p className="ant-upload-text">Click or drag file to this area to upload</p>
        </Upload.Dragger>
    );
};

export default FilesUpload;
