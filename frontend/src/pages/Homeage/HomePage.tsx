import { useMsal } from '@azure/msal-react';
import React, { useEffect, useState } from 'react';
import { loginRequest } from '../../authConfig';
import FilesList from '../../components/FilesList/FilesList';
import FilesUpload from '../../components/FilesUpload/FilesUpload';
import { RmpFile, fetchFiles, getMatchingResults, uploadFiles } from '../../services/fileService';
import styles from './HomePage.module.css';

const HomePage: React.FC = () => {
  const { instance, accounts, inProgress } = useMsal();
  const [files, setFiles] = useState<RmpFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<RmpFile | null>(null);
  const [matchingResults, setMatchingResults] = useState<{ [key: string]: number }>({});
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState<string | null>(null);

  // Get user ID from claims
  const account = accounts[0];
  const claims = account?.idTokenClaims as { oid?: string };
  const user_id = claims?.oid || '1'; // Fallback to '1' for development

  useEffect(() => {
    const initializeAuth = async () => {
      if (!account && inProgress === 'none') {
        try {
          await instance.loginRedirect(loginRequest);
        } catch (error) {
          console.error('Login failed:', error);
          setAuthError('Failed to initialize authentication');
        }
      }
    };

    initializeAuth();
  }, [account, inProgress, instance]);

  useEffect(() => {
    const loadFiles = async () => {
      if (!account || inProgress !== 'none') {
        return;
      }

      setIsLoading(true);
      try {
        const response = await fetchFiles(user_id, account, instance);
        setFiles(response);
        setAuthError(null);
      } catch (error) {
        console.error('Error loading files:', error);
        if (error instanceof Error && error.message.includes('401')) {
          setAuthError('Authentication failed. Please try logging in again.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadFiles();
  }, [user_id, account, instance, inProgress]);

  useEffect(() => {
    const fetchMatchingResults = async () => {
      if (!selectedFile || !account || inProgress !== 'none') {
        return;
      }

      try {
        const results = await getMatchingResults(
          user_id,
          selectedFile.id,
          selectedFile.type,
          account,
          instance
        );
        const matchScores = results.reduce((acc, result) => {
          const targetFile = selectedFile.type === 'CV' ? result.jd : result.cv;
          acc[targetFile.id] = result.overall_match_percentage;
          return acc;
        }, {} as { [key: string]: number });
        setMatchingResults(matchScores);
        setAuthError(null);
      } catch (error) {
        console.error('Error fetching matching results:', error);
        if (error instanceof Error && error.message.includes('401')) {
          setAuthError('Authentication failed. Please try logging in again.');
        }
      }
    };

    fetchMatchingResults();
  }, [selectedFile, user_id, account, instance, inProgress]);

  const handleFilesUploaded = async (uploadedFiles: File[], fileType: string) => {
    if (!account || inProgress !== 'none') {
      return;
    }

    try {
      const response = await uploadFiles(uploadedFiles, user_id, fileType, account, instance);
      const rmp_files = response.files.map(file => ({
        id: `temp-${Date.now()}-${file.name}`,
        filename: file.name,
        type: fileType,
        user_id: user_id,
        url: URL.createObjectURL(file),
        text: ''
      } as RmpFile));
      setFiles(prevFiles => [...prevFiles, ...rmp_files]);
      setAuthError(null);
    } catch (error) {
      console.error('Error uploading files:', error);
      if (error instanceof Error && error.message.includes('401')) {
        setAuthError('Authentication failed. Please try logging in again.');
      }
    }
  };

  const handleFileSelect = (file: RmpFile) => {
    setSelectedFile(file);
  };

  const handleLogin = async () => {
    try {
      await instance.loginRedirect(loginRequest);
    } catch (error) {
      console.error('Login failed:', error);
      setAuthError('Failed to initialize login');
    }
  };

  const cvFiles = files.filter(file => file.type === 'CV');
  const jdFiles = files.filter(file => file.type === 'JD');

  if (inProgress !== 'none') {
    return <div>Authentication in progress...</div>;
  }

  if (authError) {
    return (
      <div>
        <p>{authError}</p>
        <button onClick={handleLogin}>Login Again</button>
      </div>
    );
  }

  if (!account) {
    return (
      <div>
        <p>Please sign in to access this page.</p>
        <button onClick={handleLogin}>Login</button>
      </div>
    );
  }

  if (isLoading) {
    return <div>Loading...</div>;
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
            fileType="JD"
            setFiles={setFiles}
            selectedFile={selectedFile}
            matchingScores={selectedFile?.type === 'CV' ? matchingResults : {}}
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
            fileType="CV"
            setFiles={setFiles}
            selectedFile={selectedFile}
            matchingScores={selectedFile?.type === 'JD' ? matchingResults : {}}
          />
        </div>
      </div>
    </div>
  );
};

export default HomePage;
