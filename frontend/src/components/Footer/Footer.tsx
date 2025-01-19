// File: src/components/Footer/Footer.tsx

import React from 'react';
import Logo from '../Logo/Logo';
import styles from './Footer.module.css';

const Footer: React.FC = () => {
  return (
    <footer className={styles.wrapper}>
      <div className={styles.footerInner}>
        <Logo className={styles.footerLogo} />
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
