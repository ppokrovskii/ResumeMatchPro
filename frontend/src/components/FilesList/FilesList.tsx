import { DeleteOutlined, StarFilled, StarOutlined } from '@ant-design/icons';
import { Button, List } from 'antd';
import React from 'react';
import { RmpFile } from '../../services/fileService';
import styles from './FilesList.module.css';

interface FilesListProps {
  files: RmpFile[];
  onFileSelect: (file: RmpFile) => void;
  fileType: string;
  setFiles: React.Dispatch<React.SetStateAction<RmpFile[]>>;
  selectedFile: RmpFile | null;
  matchingScores: { [key: string]: number };
}

const FilesList: React.FC<FilesListProps> = ({
  files,
  onFileSelect,
  selectedFile,
  matchingScores,
  setFiles
}) => {
  const handleDelete = (fileId: string) => {
    setFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
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
