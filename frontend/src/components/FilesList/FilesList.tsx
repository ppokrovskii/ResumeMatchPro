import React from 'react';

import { RmpFile } from '../../services/fileService';

interface FilesListProps {
  files: RmpFile[];
  onFileSelect: (fileId: string, fileType: string) => void;
  fileType: string;
}

const FilesList: React.FC<FilesListProps> = ({ files, onFileSelect, fileType }) => {
  return (
    <ul>
      {files.map(file => (
        <li
          key={file.id}
          onClick={() => onFileSelect(file.id, fileType)}
          style={{ cursor: 'pointer' }}
        >
          {file.filename}
        </li>
      ))}
    </ul>
  );
};

export default FilesList;
