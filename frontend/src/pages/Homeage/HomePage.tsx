import { useMsal } from '@azure/msal-react';
import { message } from 'antd';
import React, { useContext, useState } from 'react';
import FileDetails from '../../components/FileDetails/FileDetails';
import FilesList from '../../components/FilesList/FilesList';
import FilesUpload from '../../components/FilesUpload/FilesUpload';
import { AuthContext } from '../../contexts/AuthContext';
import { useFiles } from '../../hooks/useFiles';
import { getFile, getMatchingResults, RmpFile } from '../../services/fileService';
import styles from './HomePage.module.css';

interface ColumnState {
  isShowingDetails: boolean;
  selectedFile: RmpFile | null;
  fileDetails: RmpFile | null;
}

const HomePage: React.FC = () => {
  const { isAuthenticated, user, isInitialized } = useContext(AuthContext);
  const { instance, accounts } = useMsal();
  const { cvFiles, jdFiles, isLoading, refreshFiles } = useFiles(instance, accounts, isAuthenticated);
  const [matchingScores, setMatchingScores] = useState<{ [key: string]: number }>({});

  // Track state for each column
  const [jdColumnState, setJdColumnState] = useState<ColumnState>({
    isShowingDetails: false,
    selectedFile: null,
    fileDetails: null,
  });
  const [cvColumnState, setCvColumnState] = useState<ColumnState>({
    isShowingDetails: false,
    selectedFile: null,
    fileDetails: null,
  });

  const handleFilesUploaded = async (response: { files: { name: string }[] }, fileType: 'CV' | 'JD') => {
    if (!user) return;

    try {
      const account = accounts[0];
      if (!account) {
        throw new Error('No account found');
      }

      await refreshFiles();
      message.success('Files uploaded successfully');
    } catch (error) {
      console.error('Error handling uploaded files:', error);
      message.error('Failed to process uploaded files');
    }
  };

  const handleFileSelect = async (file: RmpFile) => {
    try {
      const account = accounts[0];
      if (!account) {
        throw new Error('No account found');
      }

      // Fetch file details first
      const fileDetails = await getFile(file.id, account, instance);

      // Update only the relevant column state without affecting the other column
      if (file.type === 'JD') {
        setJdColumnState({ isShowingDetails: true, selectedFile: file, fileDetails });
      } else {
        setCvColumnState({ isShowingDetails: true, selectedFile: file, fileDetails });
      }

      // Get matching results
      const results = await getMatchingResults(file.id, file.type, account, instance);
      const scoresMap: { [key: string]: number } = {};
      results.forEach(result => {
        const targetFile = file.type === 'CV' ? result.jd : result.cv;
        scoresMap[targetFile.id] = result.overall_match_percentage;
      });
      setMatchingScores(scoresMap);
    } catch (error) {
      console.error('Error getting file details and matching results:', error);
      message.error('Failed to load file details and matching results');
    }
  };

  if (!isInitialized) {
    return <div>Initializing authentication...</div>;
  }

  if (!isAuthenticated || !user) {
    return <div>Loading...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.columnsContainer}>
        <div className={styles.column}>
          {jdColumnState.isShowingDetails && jdColumnState.fileDetails ? (
            <FileDetails
              file={jdColumnState.fileDetails}
              onBack={() => setJdColumnState({ isShowingDetails: false, selectedFile: null, fileDetails: null })}
            />
          ) : (
            <>
              <h2 className={styles.columnTitle}>Job Descriptions</h2>
              <div className={styles.uploadSection}>
                <FilesUpload onFilesUploaded={(files) => handleFilesUploaded(files, 'JD')} fileType='JD' />
              </div>
              <FilesList
                files={jdFiles}
                onFileSelect={handleFileSelect}
                selectedFile={jdColumnState.selectedFile}
                fileType="JD"
                matchingScores={cvColumnState.selectedFile?.type === 'CV' ? matchingScores : {}}
                refreshFiles={refreshFiles}
                isLoading={isLoading}
              />
            </>
          )}
        </div>
        <div className={styles.column}>
          {cvColumnState.isShowingDetails && cvColumnState.fileDetails ? (
            <FileDetails
              file={cvColumnState.fileDetails}
              onBack={() => setCvColumnState({ isShowingDetails: false, selectedFile: null, fileDetails: null })}
            />
          ) : (
            <>
              <h2 className={styles.columnTitle}>CVs</h2>
              <div className={styles.uploadSection}>
                <FilesUpload onFilesUploaded={(files) => handleFilesUploaded(files, 'CV')} fileType='CV' />
              </div>
              <FilesList
                files={cvFiles}
                onFileSelect={handleFileSelect}
                selectedFile={cvColumnState.selectedFile}
                fileType="CV"
                matchingScores={jdColumnState.selectedFile?.type === 'JD' ? matchingScores : {}}
                refreshFiles={refreshFiles}
                isLoading={isLoading}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default HomePage;
