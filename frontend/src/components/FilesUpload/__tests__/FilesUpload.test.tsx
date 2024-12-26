import React from 'react';
import { render, screen } from '@testing-library/react';
import FilesUpload from '../FilesUpload';

jest.mock('../../../services/fileService', () => ({
    uploadFiles: jest.fn().mockResolvedValue({ files: ['file1.pdf'] })
}));

describe('FilesUpload', () => {
    const mockOnFilesUploaded = jest.fn();
    const fileType = 'resume';

    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders upload area', () => {
        render(
            <FilesUpload onFilesUploaded={mockOnFilesUploaded} fileType={fileType} />
        );
        expect(screen.getByText('Click or drag file to this area to upload')).toBeInTheDocument();
    });

    // Add more tests as needed
}); 