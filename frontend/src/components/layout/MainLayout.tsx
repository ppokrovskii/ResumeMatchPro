import React from 'react';
import Header from '../Header/Header';
import Footer from '../Footer/Footer';

interface Props {
  children: React.ReactNode;
}

export const MainLayout: React.FC<Props> = ({ children }) => (
  <div className="app">
    <Header />
    <main className="main-content">
      {children}
    </main>
    <Footer />
  </div>
); 