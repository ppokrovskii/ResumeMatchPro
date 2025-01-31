import React from 'react';
import Footer from '../Footer/Footer';
import TopNavbar from '../Nav/TopNavbar/TopNavbar';
import styles from './MainLayout.module.css';

/**
 * Props for the MainLayout component
 */
interface MainLayoutProps {
  /** The content to be rendered inside the main layout */
  children: React.ReactNode;
}

/**
 * MainLayout component that provides a consistent layout structure
 * @param {MainLayoutProps} props - The props for the component
 * @returns {JSX.Element} The rendered component
 */
const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className={styles.layout}>
      <TopNavbar />
      <main className={styles.content}>
        {children}
      </main>
      <Footer />
    </div>
  );
};

export default MainLayout; 