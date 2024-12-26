import { render, screen } from '@test-utils';
import FilesUpload from '../FilesUpload';

describe('FilesUpload', () => {
  it('renders upload area', () => {
    render(
      <FilesUpload 
        onFilesUploaded={() => {}} 
        fileType="resume"
      />
    );
    expect(screen.getByText('Click or drag file to this area to upload')).toBeInTheDocument();
  });
});