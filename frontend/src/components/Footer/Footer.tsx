// File: src/components/Footer/Footer.tsx

import React from 'react';
import styles from './Footer.module.css';

const Footer: React.FC = () => {
  return (
    <footer className={styles.appFooter}>
      <div className={styles.footerContent}>
        <div className={styles.logo}>
          ResumeMatch Pro
        </div>
        <ul className={styles.footerLinks}>
          <li><a href="/privacy">Privacy Policy</a></li>
          <li><a href="/terms">Terms of Service</a></li>
          <li><a href="/contact">Contact Us</a></li>
        </ul>
      </div>
    </footer>
  );
};

export default Footer;
