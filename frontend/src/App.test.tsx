import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders learn react link', () => {
  render(<App />);
  // find div with class 'app'
  const appDiv = screen.getByRole('main');
  expect(appDiv).toBeInTheDocument();
}
);

