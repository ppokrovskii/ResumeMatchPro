import { DeleteOutlined, StarFilled, StarOutlined } from '@ant-design/icons';
import { useMsal } from '@azure/msal-react';
import { Button, List, message } from 'antd';
import React, { useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import { RmpFile, deleteFile } from '../../services/fileService';
import styles from './FilesList.module.css';

interface FilesListProps {
  files: RmpFile[];
  onFileSelect: (file: RmpFile) => void;
  selectedFile: RmpFile | null;
  fileType: string;
  matchingScores: { [key: string]: number };
  setFiles?: React.Dispatch<React.SetStateAction<RmpFile[]>>;
}

const FilesList: React.FC<FilesListProps> = ({
  files,
  onFileSelect,
  selectedFile,
  matchingScores,
  setFiles
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
      if (setFiles) {
        setFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
      }
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
    <List
      className={styles.filesList}
      itemLayout="horizontal"
      dataSource={files}
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
  );
};

export default FilesList;
