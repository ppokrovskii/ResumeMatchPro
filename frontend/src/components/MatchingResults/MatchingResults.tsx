import React, { useEffect, useState } from 'react';
import { getMatchingResults } from '../../services/fileService';


interface SelectedFile {
  id: string;
  type: string;
}

const MatchingResults = ({ user_id, selectedFile }: { user_id: string; selectedFile: SelectedFile }) => {
  const [results, setResults] = useState<any[]>([]);

  useEffect(() => {
    // Adjusted to use both file ID and type
    getMatchingResults(user_id, selectedFile.id, selectedFile.type).then((response: any[]) => setResults(response));
    }, [user_id, selectedFile.id, selectedFile.type]);

  return (
    <ul>
      {results.map(result => (
        <li key={result.id}>
            <p>CV {result.cv.filename} vs JD {result.jd.filename}</p>
            <p>Overall match percentage: {result.overall_match_percentage}</p>
            <p>Skills match: {result.cv_match.skills_match.join(', ')}</p>
            <p>Experience match: {result.cv_match.experience_match.join(', ')}</p>
            <p>Education match: {result.cv_match.education_match.join(', ')}</p>
            <p>Gaps: {result.cv_match.gaps.join(', ')}</p>
        </li>
      ))}
    </ul>
  );
};

export default MatchingResults;
