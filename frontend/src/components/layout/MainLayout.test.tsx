import React from 'react';
import { render, screen } from '@testing-library/react';
import { MainLayout } from './MainLayout';

// Mock the Header and Footer components
jest.mock('../Header/Header', () => ({
  __esModule: true,
  default: () => <div>Header</div>
}));

jest.mock('../Footer/Footer', () => ({
  __esModule: true,
  default: () => <div>Footer</div>
}));

describe('MainLayout', () => {
  it('renders header, content and footer', () => {
    render(
      <MainLayout>
        <div>Main Content</div>
      </MainLayout>
    );

    expect(screen.getByText('Header')).toBeInTheDocument();
    expect(screen.getByText('Main Content')).toBeInTheDocument();
    expect(screen.getByText('Footer')).toBeInTheDocument();
  });

  it('applies correct CSS classes', () => {
    render(
      <MainLayout>
        <div>Test Content</div>
      </MainLayout>
    );

    expect(document.querySelector('.app')).toBeInTheDocument();
    expect(document.querySelector('.main-content')).toBeInTheDocument();
  });
}); 