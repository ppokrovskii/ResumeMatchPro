import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import FilesList from '../FilesList';
import { RmpFile } from '../../../services/fileService';

const mockFiles: RmpFile[] = [
  {
    id: '1',
    filename: 'file1.txt',
    type: 'txt',
    user_id: '1',
    url: 'file1.txt',
    text: ''
  }
];

test('renders a list of files', () => {
  render(
    <FilesList 
      files={mockFiles} 
      onFileSelect={() => {}} 
      fileType="JD" 
      setFiles={() => {}}
      handleFilesUploaded={() => {}}
    />
  );

  const fileItems = screen.getAllByRole('listitem');
  expect(fileItems).toHaveLength(mockFiles.length);
  expect(fileItems[0]).toHaveTextContent('file1.txt');
});

test('calls onFileSelect when a file is clicked', () => {
  const mockOnFileSelect = jest.fn();
  render(
    <FilesList 
      files={mockFiles} 
      onFileSelect={mockOnFileSelect} 
      fileType="CV"
      setFiles={() => {}}
      handleFilesUploaded={() => {}}
    />
  );

  const fileItem = screen.getByText('file1.txt');
  fireEvent.click(fileItem);

  expect(mockOnFileSelect).toHaveBeenCalledTimes(1);
  expect(mockOnFileSelect).toHaveBeenCalledWith(mockFiles[0]);
});

test('renders files with correct type', () => {
  const jdFiles: RmpFile[] = [{
    ...mockFiles[0],
    type: 'JD'
  }];

  render(
    <FilesList 
      files={jdFiles} 
      onFileSelect={() => {}} 
      fileType="JD"
      setFiles={() => {}}
      handleFilesUploaded={() => {}}
    />
  );

  const fileItems = screen.getAllByRole('listitem');
  expect(fileItems).toHaveLength(1);
  expect(fileItems[0]).toHaveTextContent('file1.txt');
}); 