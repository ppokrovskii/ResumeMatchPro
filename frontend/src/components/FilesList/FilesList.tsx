import React from 'react';

import { RmpFile } from '../../services/fileService';
import FilesUpload from '../FilesUpload/FilesUpload';

interface FilesListProps {
  files: RmpFile[];
  onFileSelect: (fileId: string, fileType: string) => void;
  fileType: string;
}

const user_id = '1'; // Normally taken from global state or props

function onFilesUploaded(files: File[], fileType: string): void {
    // convert the array of File objects to an array of RmpFile objects
    const rmp_files = files.map(file => ({
      id: file.name,
      filename: file.name,
      type: fileType,
      user_id,
      url: URL.createObjectURL(file),
      text: '', // initialize the text to an empty string
    } as RmpFile)); // Cast each object to RmpFile
    // add the new files to the existing files
    setFiles(prevFiles => [...prevFiles, ...rmp_files]);
  }

const FilesList: React.FC<FilesListProps> = ({ files, onFileSelect, fileType }) => {
  return (
    <div>
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
    <FilesUpload onFilesUploaded={onFilesUploaded} fileType='CV' />
    </div>
  );
};

export default FilesList;
