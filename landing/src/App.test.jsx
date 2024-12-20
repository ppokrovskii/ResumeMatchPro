import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the Carousel component to avoid matchMedia issues
jest.mock('./components/Carousel/Carousel', () => {
  return function DummyCarousel() {
    return <div>Carousel Mock</div>;
  };
});

describe('App Component', () => {
  it('renders main sections', () => {
    render(<App />);
    
    // Test that main sections are rendered
    expect(screen.getByText(/Speed Up Recruitment/i)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Increase Your Chances of Landing an Interview/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /How it works/i, level: 1 })).toBeInTheDocument();
  });

  it('renders navigation elements', () => {
    render(<App />);
    
    expect(screen.getAllByText(/Get Early Access/i)[0]).toBeInTheDocument();
    expect(screen.getAllByRole('navigation')[0]).toBeInTheDocument();
  });
}); 