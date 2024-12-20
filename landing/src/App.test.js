import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the Carousel component since we don't need to test its functionality here
jest.mock('./components/Carousel/Carousel', () => {
  return function DummyCarousel() {
    return <div data-testid="mock-carousel">Carousel Mock</div>;
  };
});

describe('App Component', () => {
  it('renders without crashing', () => {
    render(<App />);
    expect(screen.getByTestId('mock-carousel')).toBeInTheDocument();
  });

  it('renders main landing page', () => {
    render(<App />);
    // Test for key elements that should be present
    expect(screen.getByText(/Speed Up Recruitment/i)).toBeInTheDocument();
  });
});
