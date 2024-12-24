import React from 'react';
import { RmpFile } from '../../services/fileService';
import FilesUpload from '../FilesUpload/FilesUpload';

interface FilesListProps {
  files: RmpFile[];
  onFileSelect: (file: RmpFile) => void;
  fileType: string;
  setFiles: React.Dispatch<React.SetStateAction<RmpFile[]>>;
  handleFilesUploaded: (files: File[], fileType: string) => void;
}

const FilesList: React.FC<FilesListProps> = ({ 
  files, 
  onFileSelect, 
  fileType, 
  handleFilesUploaded 
}) => {
  return (
    <div>
      <ul>
        {files.map(file => (
          <li
            key={file.id}
            onClick={() => onFileSelect(file)}
            style={{ cursor: 'pointer' }}
          >
            {file.filename}
          </li>
        ))}
      </ul>
      <FilesUpload 
        onFilesUploaded={(files) => handleFilesUploaded(files, fileType)} 
        fileType={fileType} 
      />
    </div>
  );
};

export default FilesList;
