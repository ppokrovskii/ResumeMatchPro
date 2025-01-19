import { useMsal } from '@azure/msal-react';
import { message } from 'antd';
import React, { useContext, useEffect, useState } from 'react';
import FilesList from '../../components/FilesList/FilesList';
import FilesUpload from '../../components/FilesUpload/FilesUpload';
import { AuthContext } from '../../contexts/AuthContext';
import { fetchFiles, RmpFile } from '../../services/fileService';
import styles from './HomePage.module.css';

interface IdTokenClaims {
  sub: string;
  [key: string]: unknown;
}

const HomePage: React.FC = () => {
  const { isAuthenticated, user, login, isInitialized } = useContext(AuthContext);
  const { instance, accounts } = useMsal();
  const [selectedFile, setSelectedFile] = useState<RmpFile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [cvFiles, setCvFiles] = useState<RmpFile[]>([]);
  const [jdFiles, setJdFiles] = useState<RmpFile[]>([]);
  const [matchingScores, setMatchingScores] = useState<{ [key: string]: number }>({});

  useEffect(() => {
    if (!isInitialized) return;

    if (!isAuthenticated) {
      login();
      return;
    }

    const loadFiles = async () => {
      try {
        setIsLoading(true);
        if (accounts.length > 0) {
          const account = accounts[0];
          // Get ID token claims to get the sub claim
          const response = await instance.acquireTokenSilent({
            scopes: ['openid'],
            account: account
          });
          const claims = response.idTokenClaims as IdTokenClaims;
          const userId = claims.sub;
          if (!userId) {
            throw new Error('No user ID found in token claims');
          }
          const loadedFiles = await fetchFiles(userId, account, instance);
          setCvFiles(loadedFiles.filter((file: RmpFile) => file.type === 'CV'));
          setJdFiles(loadedFiles.filter((file: RmpFile) => file.type === 'JD'));
        }
      } catch (error) {
        console.error('Error loading files:', error);
        message.error('Failed to load files');
      } finally {
        setIsLoading(false);
      }
    };

    loadFiles();
  }, [isInitialized, isAuthenticated, user, login, instance, accounts]);

  const handleFilesUploaded = async (response: { files: { name: string }[] }, fileType: 'CV' | 'JD') => {
    if (!user) return;

    try {
      // Get ID token claims to get the sub claim for the uploaded files
      const account = accounts[0];
      const tokenResponse = await instance.acquireTokenSilent({
        scopes: ['openid'],
        account: account
      });
      const claims = tokenResponse.idTokenClaims as IdTokenClaims;
      const userId = claims.sub;
      if (!userId) {
        throw new Error('No user ID found in token claims');
      }

      const rmp_files = response.files.map(file => ({
        id: `temp-${Date.now()}-${file.name}`,
        filename: file.name,
        type: fileType,
        user_id: userId,
        url: '', // We'll need to get the URL from the backend
        text: ''
      } as RmpFile));

      if (fileType === 'CV') {
        setCvFiles(prevFiles => [...prevFiles, ...rmp_files]);
      } else {
        setJdFiles(prevFiles => [...prevFiles, ...rmp_files]);
      }
    } catch (error) {
      console.error('Error handling uploaded files:', error);
      message.error('Failed to process uploaded files');
    }
  };

  const handleFileSelect = async (file: RmpFile) => {
    try {
      setSelectedFile(file);
      // We'll need to update getMatchingResults to work with our new auth system
      // const results = await getMatchingResults(user?.name || '', file.id, file.type);
      // For now, just clear matching scores when selecting a new file
      setMatchingScores({});
    } catch (error) {
      console.error('Error getting matching results:', error);
      message.error('Failed to get matching results');
    }
  };

  if (!isInitialized) {
    return <div>Initializing authentication...</div>;
  }

  if (!isAuthenticated || !user) {
    return <div>Loading...</div>;
  }

  if (isLoading) {
    return <div>Loading files...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.columnsContainer}>
        <div className={styles.column}>
          <h2 className={styles.columnTitle}>Job Descriptions</h2>
          <div className={styles.uploadSection}>
            <FilesUpload onFilesUploaded={(files) => handleFilesUploaded(files, 'JD')} fileType='JD' />
          </div>
          <FilesList
            files={jdFiles}
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
            fileType="JD"
            setFiles={setJdFiles}
            matchingScores={selectedFile?.type === 'CV' ? matchingScores : {}}
          />
        </div>
        <div className={styles.column}>
          <h2 className={styles.columnTitle}>CVs</h2>
          <div className={styles.uploadSection}>
            <FilesUpload onFilesUploaded={(files) => handleFilesUploaded(files, 'CV')} fileType='CV' />
          </div>
          <FilesList
            files={cvFiles}
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
            fileType="CV"
            setFiles={setCvFiles}
            matchingScores={selectedFile?.type === 'JD' ? matchingScores : {}}
          />
        </div>
      </div>
    </div>
  );
};

export default HomePage;
