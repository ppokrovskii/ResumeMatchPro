import React, { useEffect, useState } from 'react';
import { File, fetchFiles } from '../../services/fileService';
import FilesList from '../../components/FilesList/FilesList';
import MatchingResults from '../../components/MatchingResults/MatchingResults';


const HomePage = () => {

  const [files, setFiles] = useState<File[]>([]); // Specify the type of the state variable as an array of File objects
  const [selectedFile, setSelectedFile] = useState<{ id: string; type: string } | null>(null);
  const user_id = '1'; // Replace with the actual user ID

  useEffect(() => {
    fetchFiles(user_id).then((response: File[]) => setFiles(response)); // Specify the type of the response from fetchFiles
  }, []);

  function handleFileSelect(fileId: string, fileType: string): void {
    setSelectedFile({ id: fileId, type: fileType });
  }

  return (
    <div>
      <FilesList files={files.filter(file => file.type === 'CV')} onFileSelect={handleFileSelect} fileType="CV" />
      <FilesList files={files.filter(file => file.type === 'JD')} onFileSelect={handleFileSelect} fileType="JD" />
      {selectedFile && selectedFile.id && <MatchingResults user_id={user_id} selectedFile={selectedFile} />}
    </div>
  );
};

export default HomePage;
