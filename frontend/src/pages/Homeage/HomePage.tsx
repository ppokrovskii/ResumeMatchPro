import React, { useEffect, useState } from 'react';
import { RmpFile, fetchFiles } from '../../services/fileService';
import FilesList from '../../components/FilesList/FilesList';
import MatchingResults from '../../components/MatchingResults/MatchingResults';
import FilesUpload from '../../components/FilesUpload/FilesUpload';


const HomePage: React.FC = () => {

  const [files, setFiles] = useState<RmpFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<RmpFile | null>(null);
  const user_id = "some-user-id"; // Replace with actual user ID logic

  useEffect(() => {
    fetchFiles(user_id).then((response: RmpFile[]) => setFiles(response));
  }, []);

  const handleFileSelect = (file: RmpFile) => {
    setSelectedFile(file);
  };

  const handleFilesUploaded = (uploadedFiles: File[], fileType: string) => {
    const rmp_files = uploadedFiles.map(file => ({
      id: `temp-${Date.now()}-${file.name}`,
      filename: file.name,
      type: fileType,
      user_id: user_id,
      url: URL.createObjectURL(file),
      text: ''
    } as RmpFile));
    setFiles(prevFiles => [...prevFiles, ...rmp_files]);
  };

  return (
    <div>
      <div>
        <FilesList 
          files={files.filter(file => file.type === 'CV')} 
          onFileSelect={handleFileSelect} 
          fileType="CV"
          setFiles={setFiles}
          handleFilesUploaded={handleFilesUploaded}
        />
        <FilesUpload onFilesUploaded={(files) => handleFilesUploaded(files, 'CV')} fileType='CV' />
        <FilesList 
          files={files.filter(file => file.type === 'JD')} 
          onFileSelect={handleFileSelect} 
          fileType="JD"
          setFiles={setFiles}
          handleFilesUploaded={handleFilesUploaded}
        />
      </div>
      <FilesUpload onFilesUploaded={(files) => handleFilesUploaded(files, 'JD')} fileType='JD' />
      {selectedFile && selectedFile.id && <MatchingResults user_id={user_id} selectedFile={selectedFile} />}
    </div>
  );
};

export default HomePage;
