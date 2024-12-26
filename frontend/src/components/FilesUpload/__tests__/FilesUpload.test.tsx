import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import FilesUpload from '../FilesUpload';
import { uploadFiles } from '../../../services/fileService';

// Mock the fileService
jest.mock('../../../services/fileService');

// Define the mock file outside the describe block
const mockFile = new File(['dummy content'], 'example.pdf', { type: 'application/pdf' });

// Mock antd Upload component
jest.mock('antd', () => ({
  Upload: {
    Dragger: ({ customRequest, children }: any) => (
      <div onClick={() => customRequest?.({ file: mockFile, onSuccess: jest.fn(), onError: jest.fn() })}>
        {children}
      </div>
    ),
  },
}));

describe('FilesUpload Component', () => {
  const mockOnFilesUploaded = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders upload area', () => {
    render(<FilesUpload onFilesUploaded={mockOnFilesUploaded} fileType="CV" />);
    const uploadText = screen.getByText(/click or drag file to this area to upload/i);
    expect(uploadText).toBeInTheDocument();
  });

  test('calls onFilesUploaded when file is uploaded successfully', async () => {
    const mockResponse = { files: [mockFile] };
    (uploadFiles as jest.Mock).mockResolvedValue(mockResponse);

    render(<FilesUpload onFilesUploaded={mockOnFilesUploaded} fileType="CV" />);
    
    // Trigger upload
    const uploadArea = screen.getByText(/click or drag file to this area to upload/i);
    uploadArea.click();

    await waitFor(() => {
      expect(uploadFiles).toHaveBeenCalledWith([mockFile], '1', 'CV');
    });

    await waitFor(() => {
      expect(mockOnFilesUploaded).toHaveBeenCalledWith(mockResponse.files, 'CV');
    });
  });

  test('handles upload error', async () => {
    const mockError = new Error('Upload failed');
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    (uploadFiles as jest.Mock).mockRejectedValue(mockError);

    render(<FilesUpload onFilesUploaded={mockOnFilesUploaded} fileType="CV" />);
    
    // Trigger upload
    const uploadArea = screen.getByText(/click or drag file to this area to upload/i);
    uploadArea.click();

    await waitFor(() => {
      expect(uploadFiles).toHaveBeenCalledWith([mockFile], '1', 'CV');
    });

    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith('Error uploading files:', mockError);
    });

    consoleErrorSpy.mockRestore();
  });
}); 