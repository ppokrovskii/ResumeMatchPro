import { useMsal } from '@azure/msal-react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { uploadFiles } from '../../../services/fileService';
import FilesUpload from '../FilesUpload';

// Mock the file service
jest.mock('../../../services/fileService');
jest.mock('@azure/msal-react');

describe('FilesUpload', () => {
  const mockOnFilesUploaded = jest.fn();
  const mockAccount = {
    idTokenClaims: { sub: 'test-user-id' }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (useMsal as jest.Mock).mockReturnValue({
      instance: {},
      accounts: [mockAccount]
    });
  });

  it('should upload file only once', async () => {
    // Mock successful upload
    (uploadFiles as jest.Mock).mockResolvedValue({ files: [{ name: 'test.pdf' }] });

    render(
      <FilesUpload
        onFilesUploaded={mockOnFilesUploaded}
        fileType="CV"
      />
    );

    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByText(/click or drag file/i);

    // Simulate file drop
    fireEvent.drop(input, {
      dataTransfer: {
        files: [file]
      }
    });

    await waitFor(() => {
      expect(uploadFiles).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      expect(uploadFiles).toHaveBeenCalledWith(
        [file],
        'test-user-id',
        'CV',
        mockAccount,
        expect.anything()
      );
    });

    expect(mockOnFilesUploaded).toHaveBeenCalledTimes(1);
  });
});