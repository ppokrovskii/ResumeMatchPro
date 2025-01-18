import { fireEvent, render, screen } from '@test-utils';
import { RmpFile } from '../../../services/fileService';
import FilesList from '../FilesList';

describe('FilesList', () => {
  const mockFiles: RmpFile[] = [
    { id: '1', filename: 'test1.pdf', type: 'resume', user_id: '1', url: 'test1.pdf', text: '' },
    { id: '2', filename: 'test2.pdf', type: 'resume', user_id: '1', url: 'test2.pdf', text: '' },
  ];

  const mockMatchingScores = {
    '1': 80,
    '2': 60
  };

  it('renders list of files', () => {
    render(
      <FilesList
        files={mockFiles}
        onFileSelect={() => { }}
        fileType="resume"
        setFiles={() => { }}
        selectedFile={null}
        matchingScores={mockMatchingScores}
      />
    );

    expect(screen.getByText('test1.pdf')).toBeInTheDocument();
    expect(screen.getByText('test2.pdf')).toBeInTheDocument();
    expect(screen.getByText('80%')).toBeInTheDocument();
    expect(screen.getByText('60%')).toBeInTheDocument();
  });

  it('calls onFileSelect when a file is clicked', () => {
    const onFileSelect = jest.fn();
    render(
      <FilesList
        files={mockFiles}
        onFileSelect={onFileSelect}
        fileType="resume"
        setFiles={() => { }}
        selectedFile={null}
        matchingScores={mockMatchingScores}
      />
    );

    const fileItem = screen.getByText('test1.pdf');
    fireEvent.click(fileItem);

    expect(onFileSelect).toHaveBeenCalledWith(mockFiles[0]);
  });
}); 