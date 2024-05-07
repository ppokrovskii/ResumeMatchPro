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

  return (
    <div>
      <div style={{ display: 'flex', flexDirection: 'row' }}>
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
