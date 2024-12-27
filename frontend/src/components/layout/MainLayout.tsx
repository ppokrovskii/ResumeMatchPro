import React from 'react';
import Footer from '../Footer/Footer';
import Header from '../Header/Header';

/**
 * Props for the MainLayout component
 */
interface Props {
  /** The content to be rendered inside the main layout */
  children: React.ReactNode;
}

/**
 * MainLayout component that provides the common layout structure for the application
 * including header, main content area, and footer.
 */
export const MainLayout: React.FC<Props> = ({ children }) => (
  <div className="app">
    <Header />
    <main className="main-content">
      {children}
    </main>
    <Footer />
  </div>
); 