import { DeleteOutlined, StarFilled, StarOutlined } from '@ant-design/icons';
import { useMsal } from '@azure/msal-react';
import { Button, List, message, Spin } from 'antd';
import React, { useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import { deleteFile, RmpFile } from '../../services/fileService';
import styles from './FilesList.module.css';

interface FilesListProps {
  files: RmpFile[];
  onFileSelect: (file: RmpFile) => void;
  selectedFile: RmpFile | null;
  fileType: string;
  matchingScores: { [key: string]: number };
  refreshFiles: () => Promise<void>;
  isLoading?: boolean;
}

const FilesList: React.FC<FilesListProps> = ({
  files,
  onFileSelect,
  selectedFile,
  fileType,
  matchingScores,
  refreshFiles,
  isLoading = false
}) => {
  const { instance, accounts } = useMsal();
  const { isAuthenticated } = useContext(AuthContext);

  const handleDelete = async (fileId: string) => {
    if (!isAuthenticated || !accounts[0]) {
      message.error('You must be authenticated to delete files');
      return;
    }

    try {
      await deleteFile(fileId, accounts[0], instance);
      await refreshFiles();
      message.success('File deleted successfully');
    } catch (error) {
      console.error('Error deleting file:', error);
      message.error('Failed to delete file');
    }
  };

  const renderStarRating = (score: number) => {
    const stars = [];
    const fullStars = Math.floor(score / 20); // Convert percentage to 5-star scale

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <StarFilled key={i} className={styles.starFilled} />
        );
      } else {
        stars.push(
          <StarOutlined key={i} className={styles.starOutline} />
        );
      }
    }

    return (
      <div className={styles.ratingContainer}>
        <div className={styles.stars}>{stars}</div>
        <span className={styles.percentage}>{Math.round(score)}%</span>
      </div>
    );
  };

  return (
    <div className={styles.filesListWrapper}>
      <Spin spinning={isLoading} tip="Loading files...">
        <List
          className={styles.filesList}
          itemLayout="horizontal"
          dataSource={files}
          locale={{ emptyText: isLoading ? ' ' : 'No files found' }}
          renderItem={file => (
            <List.Item
              className={`${styles.fileItem} ${selectedFile?.id === file.id ? styles.selected : ''}`}
              actions={[
                <Button
                  key="delete"
                  icon={<DeleteOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(file.id);
                  }}
                  className={styles.deleteButton}
                />
              ]}
              onClick={() => onFileSelect(file)}
            >
              <List.Item.Meta
                title={file.filename}
                description={
                  matchingScores[file.id] !== undefined &&
                  renderStarRating(matchingScores[file.id])
                }
              />
            </List.Item>
          )}
        />
      </Spin>
    </div>
  );
};

export default FilesList;
