import React, { useEffect, useState } from 'react';
import {getFiles} from '../services/filesService';

const FilesPage = () => {
    const [files, setFiles] = useState([]);

    useEffect(() => {
        const fetchFiles = async () => {
            const data = await getFiles('1', 'CV');
            setFiles(data);
        };

        fetchFiles();
    }, []);

    return (
        <div style={{ maxWidth: '800px', margin: 'auto', padding: '20px' }}>
            <h1>Files</h1>
            <p>
                Below are the files available for download. Click on the file name to download the file.
            </p>
            <ul>
                {files.map((file) => (
                    <li key={file.id}>
                        <a href={file.url} download={file.name}>{file.name}</a>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default FilesPage;