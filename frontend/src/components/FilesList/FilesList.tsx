import { DeleteOutlined, LoadingOutlined, StarFilled, StarOutlined } from '@ant-design/icons';
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

  // Custom spinner icon with larger size
  const antIcon = <LoadingOutlined style={{ fontSize: 24 }} spin />;

  const renderItem = (item: RmpFile) => {
    const isSelected = selectedFile?.id === item.id;
    const hasMatchingScore = matchingScores[item.id] !== undefined;
    const score = matchingScores[item.id] || 0;

    // Display formatted name based on available fields
    const displayName = () => {
      if (item.type === 'CV' && item.name && item.job_title) {
        return `${item.name} - ${item.job_title}`;
      } else if (item.type === 'CV' && item.name) {
        return item.name;
      } else if (item.type === 'JD' && item.job_title) {
        return item.job_title;
      } else {
        return item.filename;
      }
    };

    return (
      <List.Item
        key={item.id}
        className={`${styles.fileItem} ${isSelected ? styles.selectedFile : ''}`}
        onClick={() => onFileSelect(item)}
        actions={[
          <Button
            key="delete"
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={(e) => {
              e.stopPropagation();
              handleDelete(item.id);
            }}
          />
        ]}
      >
        <List.Item.Meta
          title={
            <div className={styles.titleWrapper}>
              {displayName()}
            </div>
          }
        />
        {hasMatchingScore && fileType === 'CV' && (
          <div className={styles.scoreContainer}>
            {[1, 2, 3, 4, 5].map((star) => renderStarRating(star))}
            <span className={styles.scoreText}>{Math.round(score)}%</span>
          </div>
        )}
      </List.Item>
    );
  };

  return (
    <div className={styles.filesListWrapper}>
      <Spin spinning={isLoading} tip="Loading files..." indicator={antIcon}>
        <List
          className={styles.filesList}
          itemLayout="horizontal"
          dataSource={files.sort((a, b) => {
            const scoreA = matchingScores[a.id] || 0;
            const scoreB = matchingScores[b.id] || 0;
            return scoreB - scoreA;
          })}
          locale={{ emptyText: isLoading ? ' ' : 'No files found' }}
          renderItem={renderItem}
        />
      </Spin>
    </div>
  );
};

export default FilesList;
