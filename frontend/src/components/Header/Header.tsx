// File: src/components/Header/Header.tsx

import React, { useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import styles from './Header.module.css';

const Header: React.FC = () => {
  const { isAuthenticated, user, login, logout } = useContext(AuthContext);

  return (
    <header className={styles.appHeader}>
      <div className={styles.headerContent}>
        <div className={styles.logo}>
          Resume Match Pro
        </div>
        <div className={styles.navLinks}>
          {isAuthenticated && user ? (
            <div className={styles.userInfo}>
              <span>{user.name}</span>
              <button onClick={logout} className={styles.button}>Sign Out</button>
            </div>
          ) : (
            <button onClick={login} className={styles.button}>Sign In</button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
