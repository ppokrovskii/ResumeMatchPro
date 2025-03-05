import { useMsal } from '@azure/msal-react';
import { message, Modal, Upload } from 'antd';
import { RcFile, UploadRequestOption } from 'rc-upload/lib/interface';
import React, { useContext, useRef, useState } from 'react';
import FileDetails from '../../components/FileDetails/FileDetails';
import FilesList from '../../components/FilesList/FilesList';
import UploadMessage from '../../components/UploadMessage/UploadMessage';
import { AuthContext } from '../../contexts/AuthContext';
import { useFiles } from '../../hooks/useFiles';
import { getFile, getMatchingResults, RmpFile, uploadFiles } from '../../services/fileService';
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
  const [isUploadModalVisible, setIsUploadModalVisible] = useState(false);
  const uploadingFiles = useRef<Set<string>>(new Set());
  const [fileList, setFileList] = useState<RcFile[]>([]);

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

  const handleUploadClick = () => {
    setIsUploadModalVisible(true);
  };

  const handleUploadModalCancel = () => {
    setIsUploadModalVisible(false);
    setFileList([]);
  };

  const handleFilesSelected = async (fileList: FileList) => {
    if (!isAuthenticated || !accounts.length) {
      message.error('Please sign in to upload files');
      return;
    }

    const account = accounts[0];
    if (!account) {
      message.error('No account found');
      return;
    }

    const files: RcFile[] = [];
    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i] as unknown as RcFile;
      if (file.size / 1024 / 1024 < 10) {  // 10MB size limit
        files.push(file);
      } else {
        message.error(`${file.name} is too large, please upload files smaller than 10MB.`);
      }
    }

    if (files.length === 0) return;

    try {
      message.loading('Uploading files...', 0);
      const response = await uploadFiles(files, account, instance);
      message.destroy();

      if (files.length === 1) {
        message.success(`${files[0].name} uploaded successfully`);
      } else {
        message.success(`${files.length} files uploaded successfully`);
      }

      handleFilesUploaded(response);
    } catch (error) {
      message.destroy();
      message.error('Upload failed: ' + (error instanceof Error ? error.message : String(error)));
    }
  };

  const handleUpload = async (options: UploadRequestOption) => {
    const { file, onSuccess, onError } = options;
    const rcFile = file as RcFile;

    // Check if this file is already being uploaded
    const fileKey = `${rcFile.name}-${rcFile.size}-${rcFile.lastModified}`;
    if (uploadingFiles.current.has(fileKey)) {
      return;
    }

    try {
      uploadingFiles.current.add(fileKey);
      const account = accounts[0];
      if (!account) {
        throw new Error('No account found');
      }

      const response = await uploadFiles([rcFile], account, instance);
      handleFilesUploaded(response);
      onSuccess?.(response);
      message.success(`${rcFile.name} uploaded successfully`);
      // Clear the file list after successful upload
      setFileList([]);
    } catch (error) {
      console.error('Error uploading files:', error);
      onError?.(error as Error);

      // Display user-friendly error message
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      message.error(errorMessage);
    } finally {
      uploadingFiles.current.delete(fileKey);
    }
  };

  const handleFilesUploaded = async (response: { files: { name: string }[] }) => {
    if (!user) return;

    try {
      const account = accounts[0];
      if (!account) {
        throw new Error('No account found');
      }

      await refreshFiles();
      message.success('Files uploaded successfully');
      setIsUploadModalVisible(false);
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

  const handleCloseDetails = (fileType?: string) => {
    // If fileType is provided, only close that specific column
    if (fileType === 'JD') {
      setJdColumnState({ isShowingDetails: false, selectedFile: null, fileDetails: null });
    } else if (fileType === 'CV') {
      setCvColumnState({ isShowingDetails: false, selectedFile: null, fileDetails: null });
    } else {
      // Fallback to closing both if no fileType is specified (for backward compatibility)
      setJdColumnState({ isShowingDetails: false, selectedFile: null, fileDetails: null });
      setCvColumnState({ isShowingDetails: false, selectedFile: null, fileDetails: null });
    }
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
        <>
          <div className={styles.globalUploadMessage}>
            <UploadMessage
              onUploadClick={handleUploadClick}
              onFilesSelected={handleFilesSelected}
            />
          </div>
          <div className={styles.columnsContainer}>
            <div className={styles.column}>
              {cvColumnState.isShowingDetails ? (
                <>
                  <h2>CV Details</h2>
                  <FileDetails
                    file={cvColumnState.fileDetails}
                    isLoading={!cvColumnState.fileDetails}
                    onClose={() => handleCloseDetails('CV')}
                    canRunMatching={jdFiles.length > 0}
                    onRunMatching={handleRunMatching}
                  />
                </>
              ) : (
                <>
                  <h2>CVs</h2>
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
                    onClose={() => handleCloseDetails('JD')}
                    canRunMatching={false}
                    onRunMatching={undefined}
                  />
                </>
              ) : (
                <>
                  <h2>Job Descriptions</h2>
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

          <Modal
            title="Upload Files"
            open={isUploadModalVisible}
            onCancel={handleUploadModalCancel}
            footer={null}
          >
            <Upload.Dragger
              multiple
              accept=".pdf,.docx"
              customRequest={handleUpload}
              fileList={fileList}
              onChange={({ fileList }) => setFileList(fileList as RcFile[])}
            >
              <p className="ant-upload-drag-icon">
                <i className="fas fa-inbox"></i>
              </p>
              <p className="ant-upload-text">Click or drag file to this area to upload</p>
              <p className="ant-upload-hint">
                Supports PDF and Word documents. Files will be automatically processed.
              </p>
            </Upload.Dragger>
          </Modal>
        </>
      )}
    </div>
  );
};

export default HomePage;
