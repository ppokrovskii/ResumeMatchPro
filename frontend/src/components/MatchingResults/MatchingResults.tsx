import React from 'react';

interface MatchingResult {
  score: number;
  matches: string[];
  suggestions: string[];
}

interface MatchingResultsProps {
  results: MatchingResult[];
  onClose: () => void;
}

const MatchingResults: React.FC<MatchingResultsProps> = ({ results, onClose }) => {
  return (
    <div>
      <button onClick={onClose}>Close</button>
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
