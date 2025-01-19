import { InteractionRequiredAuthError } from '@azure/msal-browser';
import { useMsal } from '@azure/msal-react';
import { message } from 'antd';
import React, { useContext, useState } from 'react';
import FilesList from '../../components/FilesList/FilesList';
import FilesUpload from '../../components/FilesUpload/FilesUpload';
import { AuthContext } from '../../contexts/AuthContext';
import { useFiles } from '../../hooks/useFiles';
import { getMatchingResults, RmpFile } from '../../services/fileService';
import styles from './HomePage.module.css';

interface IdTokenClaims {
  sub: string;
  [key: string]: unknown;
}

const HomePage: React.FC = () => {
  const { isAuthenticated, user, isInitialized } = useContext(AuthContext);
  const { instance, accounts } = useMsal();
  const { cvFiles, jdFiles, isLoading, refreshFiles } = useFiles(instance, accounts, isAuthenticated);
  const [selectedFile, setSelectedFile] = useState<RmpFile | null>(null);
  const [matchingScores, setMatchingScores] = useState<{ [key: string]: number }>({});

  const handleFilesUploaded = async (response: { files: { name: string }[] }, fileType: 'CV' | 'JD') => {
    if (!user) return;

    try {
      const account = accounts[0];
      if (!account) {
        throw new Error('No account found');
      }

      let tokenResponse;
      try {
        tokenResponse = await instance.acquireTokenSilent({
          scopes: ['openid', 'https://resumematchprob2c.onmicrosoft.com/api/Files.ReadWrite'],
          account: account
        });
      } catch (error) {
        if (error instanceof InteractionRequiredAuthError) {
          tokenResponse = await instance.acquireTokenPopup({
            scopes: ['openid', 'https://resumematchprob2c.onmicrosoft.com/api/Files.ReadWrite'],
            account: account
          });
        } else {
          throw error;
        }
      }

      const claims = tokenResponse.idTokenClaims as IdTokenClaims;
      const userId = claims.sub;
      if (!userId) {
        throw new Error('No user ID found in token claims');
      }

      // Refresh the files list after successful upload
      await refreshFiles();
      message.success('Files uploaded successfully');
    } catch (error) {
      console.error('Error handling uploaded files:', error);
      message.error('Failed to process uploaded files');
    }
  };

  const handleFileSelect = (file: RmpFile) => {
    try {
      setSelectedFile(file);

      const account = accounts[0];
      instance.acquireTokenSilent({
        scopes: ['openid'],
        account: account
      }).then(tokenResponse => {
        const claims = tokenResponse.idTokenClaims as IdTokenClaims;
        const userId = claims.sub;
        if (!userId) {
          throw new Error('No user ID found in token claims');
        }

        getMatchingResults(userId, file.id, file.type, account, instance).then(results => {
          const scoresMap: { [key: string]: number } = {};
          results.forEach(result => {
            const targetFile = file.type === 'CV' ? result.jd : result.cv;
            scoresMap[targetFile.id] = result.overall_match_percentage;
          });
          setMatchingScores(scoresMap);
        });
      }).catch(error => {
        console.error('Error getting matching results:', error);
        message.error('Failed to get matching results');
      });
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
            matchingScores={selectedFile?.type === 'CV' ? matchingScores : {}}
            refreshFiles={refreshFiles}
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
            matchingScores={selectedFile?.type === 'JD' ? matchingScores : {}}
            refreshFiles={refreshFiles}
          />
        </div>
      </div>
    </div>
  );
};

export default HomePage;
