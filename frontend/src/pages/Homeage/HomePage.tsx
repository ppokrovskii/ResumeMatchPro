import React, { useEffect, useState } from 'react';
import { RmpFile, fetchFiles } from '../../services/fileService';
import FilesList from '../../components/FilesList/FilesList';
import MatchingResults from '../../components/MatchingResults/MatchingResults';
import FilesUpload from '../../components/FilesUpload/FilesUpload';


const HomePage = () => {

  const [files, setFiles] = useState<RmpFile[]>([]); // Specify the type of the state variable as an array of File objects
  const [selectedFile, setSelectedFile] = useState<{ id: string; type: string } | null>(null);
  const user_id = '1'; // Replace with the actual user ID

  useEffect(() => {
    fetchFiles(user_id).then((response: RmpFile[]) => setFiles(response)); // Specify the type of the response from fetchFiles
  }, []);

  function handleFileSelect(fileId: string, fileType: string): void {
    setSelectedFile({ id: fileId, type: fileType });
  }

  

  return (
    <div>
      <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between' }}>
      <div style={{ width: '45%' }}>
        <h2>CVs</h2>
        {selectedFile && selectedFile?.type === 'JD' ? (<MatchingResults user_id={user_id} selectedFile={selectedFile}/>
        ) : (
          <FilesList files={files.filter(file => file.type === 'CV')} onFileSelect={handleFileSelect} fileType="CV" />
                    )}
      </div>
        <FilesList files={files.filter(file => file.type === 'CV')} onFileSelect={handleFileSelect} fileType="CV" />
        <FilesUpload onFilesUploaded={onFilesUploaded} fileType='CV' />
        <FilesList files={files.filter(file => file.type === 'JD')} onFileSelect={handleFileSelect} fileType="JD" />
      </div>
      <FilesUpload onFilesUploaded={onFilesUploaded} fileType='JD' />
      {selectedFile && selectedFile.id && <MatchingResults user_id={user_id} selectedFile={selectedFile} />}
    </div>
  );
};

export default HomePage;
