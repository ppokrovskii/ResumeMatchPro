import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import FilesList from '../components/FilesList/FilesList';


const mockFiles = [
  { id: '1', filename: 'file1.txt', type: 'txt', user_id: '1', url: 'file1.txt', text: '' },
    { id: '2', filename: 'file2.txt', type: 'txt', user_id: '1', url: 'file2.txt', text: '' },
    { id: '3', filename: 'file3.txt', type: 'txt', user_id: '1', url: 'file3.txt', text: '' },
];

test('renders a list of files', () => {
  render(<FilesList files={mockFiles} onFileSelect={() => {}} fileType="JD" />);

  const fileItems = screen.getAllByRole('listitem');
  expect(fileItems).toHaveLength(mockFiles.length);

  mockFiles.forEach((file, index) => {
    expect(fileItems[index]).toHaveTextContent(file.filename);
  });
});

test('calls onFileSelect when a file is clicked', () => {
  const mockOnFileSelect = jest.fn();
  render(<FilesList files={mockFiles} onFileSelect={mockOnFileSelect} fileType="CV" />);

  const fileItem = screen.getByText('file1.txt');
  fireEvent.click(fileItem);

  expect(mockOnFileSelect).toHaveBeenCalledTimes(1);
  expect(mockOnFileSelect).toHaveBeenCalledWith('1', 'CV');
});

test('renders a list of files of type JD', () => {
  render(<FilesList files={mockFiles} onFileSelect={() => {}} fileType="JD" />);

  const fileItems = screen.getAllByRole('listitem');
  expect(fileItems).toHaveLength(mockFiles.length);

  mockFiles.forEach((file, index) => {
    expect(fileItems[index]).toHaveTextContent(file.filename);
  });
});

test('calls onFileSelect when a file of type JD is clicked', () => {
  const mockOnFileSelect = jest.fn();
  render(<FilesList files={mockFiles} onFileSelect={mockOnFileSelect} fileType="JD" />);

  const fileItem = screen.getByText('file1.txt');
  fireEvent.click(fileItem);

  expect(mockOnFileSelect).toHaveBeenCalledTimes(1);
  expect(mockOnFileSelect).toHaveBeenCalledWith('1', 'JD');
});

test('renders a list of files of type CV', () => {
  render(<FilesList files={mockFiles} onFileSelect={() => {}} fileType="CV" />);

  const fileItems = screen.getAllByRole('listitem');
  expect(fileItems).toHaveLength(mockFiles.length);

  mockFiles.forEach((file, index) => {
    expect(fileItems[index]).toHaveTextContent(file.filename);
  });
});

test('calls onFileSelect when a file of type CV is clicked', () => {
  const mockOnFileSelect = jest.fn();
  render(<FilesList files={mockFiles} onFileSelect={mockOnFileSelect} fileType="CV" />);

  const fileItem = screen.getByText('file1.txt');
  fireEvent.click(fileItem);

  expect(mockOnFileSelect).toHaveBeenCalledTimes(1);
  expect(mockOnFileSelect).toHaveBeenCalledWith('1', 'CV');
});

