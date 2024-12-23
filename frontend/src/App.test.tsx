import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders main layout elements', () => {
  render(<App />);
  
  // Check for main structural elements
  const mainContent = screen.getByRole('main');
  expect(mainContent).toBeInTheDocument();
  expect(mainContent).toHaveClass('main-content');
});

