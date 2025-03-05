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

  const handleFilesUploaded = async (response: { files: { name: string }[] }) => {
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
      const fileType = file.type;

      // Update only the relevant column state without affecting the other column
      if (fileType === 'JD') {
        setJdColumnState({ isShowingDetails: true, selectedFile: file, fileDetails });
      } else {
        setCvColumnState({ isShowingDetails: true, selectedFile: file, fileDetails });
      }

      // Get matching results
      const results = await getMatchingResults(file.id, fileType, account, instance);
      const scoresMap: { [key: string]: number } = {};
      results.forEach(result => {
        const targetFile = fileType === 'CV' ? result.jd : result.cv;
        scoresMap[targetFile.id] = result.overall_match_percentage;
      });
      setMatchingScores(scoresMap);
    } catch (error) {
      console.error('Error getting file details and matching results:', error);
      message.error('Failed to load file details and matching results');
    }
  };

  const handleCloseDetails = () => {
    setJdColumnState({ isShowingDetails: false, selectedFile: null, fileDetails: null });
    setCvColumnState({ isShowingDetails: false, selectedFile: null, fileDetails: null });
  };

  const handleRunMatching = async () => {
    if (!user) return;

    try {
      const account = accounts[0];
      if (!account) {
        throw new Error('No account found');
      }

      // Implement the logic to run matching
      // This is a placeholder and should be replaced with the actual implementation
      message.info('Running matching...');
    } catch (error) {
      console.error('Error running matching:', error);
      message.error('Failed to run matching');
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
      {isAuthenticated && (
        <div className={styles.columnsContainer}>
          <div className={styles.column}>
            {cvColumnState.isShowingDetails ? (
              <>
                <h2>CV Details</h2>
                <FileDetails
                  file={cvColumnState.fileDetails}
                  isLoading={!cvColumnState.fileDetails}
                  onClose={handleCloseDetails}
                  canRunMatching={jdFiles.length > 0}
                  onRunMatching={handleRunMatching}
                />
              </>
            ) : (
              <>
                <h2>CVs</h2>
                <FilesUpload
                  onFilesUploaded={handleFilesUploaded}
                />
                <FilesList
                  files={cvFiles}
                  isLoading={isLoading}
                  onFileSelect={handleFileSelect}
                  selectedFile={cvColumnState.selectedFile}
                  fileType="CV"
                  matchingScores={matchingScores}
                  refreshFiles={refreshFiles}
                />
              </>
            )}
          </div>

          <div className={styles.column}>
            {jdColumnState.isShowingDetails ? (
              <>
                <h2>JD Details</h2>
                <FileDetails
                  file={jdColumnState.fileDetails}
                  isLoading={!jdColumnState.fileDetails}
                  onClose={handleCloseDetails}
                  canRunMatching={false}
                  onRunMatching={undefined}
                />
              </>
            ) : (
              <>
                <h2>Job Descriptions</h2>
                <FilesUpload
                  onFilesUploaded={handleFilesUploaded}
                />
                <FilesList
                  files={jdFiles}
                  isLoading={isLoading}
                  onFileSelect={handleFileSelect}
                  selectedFile={jdColumnState.selectedFile}
                  fileType="JD"
                  matchingScores={matchingScores}
                  refreshFiles={refreshFiles}
                />
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
