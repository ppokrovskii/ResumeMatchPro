// File: src/components/Footer/Footer.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import styles from './Footer.module.css';

const Footer: React.FC = () => {
  return (
    <footer className={styles.appFooter}>
      <div className={styles.footerContent}>
        <ul className={styles.footerLinks}>
          <li><Link to="/about">About Us</Link></li>
          <li><Link to="/privacy">Privacy Policy</Link></li>
          <li><Link to="/terms">Terms of Service</Link></li>
        </ul>
        <div className={styles.footerCopy}>
          © {new Date().getFullYear()} Resume Match Pro. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
