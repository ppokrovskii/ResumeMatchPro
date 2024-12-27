import React, { useEffect, useState } from 'react';

interface MatchingResult {
  score: number;
  matches: string[];
  suggestions: string[];
}

interface MatchingResultsProps {
  user_id: string;
  selectedFile: {
    id: string;
    filename: string;
    type: string;
    url: string;
    text: string;
  };
}

const MatchingResults: React.FC<MatchingResultsProps> = ({ user_id, selectedFile }) => {
  const [results, setResults] = useState<MatchingResult[]>([]);

  useEffect(() => {
    // TODO: Fetch matching results using user_id and selectedFile
    // For now, using mock data
    setResults([
      {
        score: 85,
        matches: ['Experience with React', 'TypeScript knowledge'],
        suggestions: ['Add more details about testing experience']
      }
    ]);
  }, [user_id, selectedFile]);

  return (
    <div>
      <h2>Matching Results for {selectedFile.filename}</h2>
      {results.map((result, index) => (
        <div key={index}>
          <h3>Match Score: {result.score}%</h3>
          <h4>Matches:</h4>
          <ul>
            {result.matches.map((match, i) => (
              <li key={i}>{match}</li>
            ))}
          </ul>
          <h4>Suggestions:</h4>
          <ul>
            {result.suggestions.map((suggestion, i) => (
              <li key={i}>{suggestion}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default MatchingResults;
