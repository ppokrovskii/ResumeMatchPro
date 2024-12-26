import React from 'react';
import { render, screen } from '@testing-library/react';
import { MainLayout } from './MainLayout';
import { BrowserRouter } from 'react-router-dom';

// Mock Header component
jest.mock('../Header/Header', () => ({
  __esModule: true,
  default: () => <div>Mock Header</div>
}));

describe('MainLayout', () => {
  it('renders header and children', () => {
    render(
      <BrowserRouter>
        <MainLayout>
          <div>Test Content</div>
        </MainLayout>
      </BrowserRouter>
    );

    expect(screen.getByText('Mock Header')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });
}); 