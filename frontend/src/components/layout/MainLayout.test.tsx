import { render, screen } from '@test-utils';
import { MainLayout } from './MainLayout';

// Mock Header component
jest.mock('../Header/Header', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-header">Mock Header</div>,
}));

// Mock Footer component
jest.mock('../Footer/Footer', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-footer">Mock Footer</div>,
}));

describe('MainLayout', () => {
  it('renders header and children', () => {
    render(
      <MainLayout>
        <div>Test Content</div>
      </MainLayout>
    );

    expect(screen.getByTestId('mock-header')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
    expect(screen.getByTestId('mock-footer')).toBeInTheDocument();
  });
});