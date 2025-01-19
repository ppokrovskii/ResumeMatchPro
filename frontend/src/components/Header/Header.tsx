// File: src/components/Header/Header.tsx

import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import Logo from '../Logo/Logo';
import styles from './Header.module.css';

const Header: React.FC = () => {
  const { isAuthenticated, user, login, logout } = useContext(AuthContext);
  const [y, setY] = useState(window.scrollY);

  useEffect(() => {
    const handleScroll = () => setY(window.scrollY);
    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [y]);

  return (
    <header
      className={styles.wrapper}
      style={y > 100 ? { height: "60px" } : { height: "80px" }}
    >
      <div className={styles.navInner}>
        <Logo />
        <div className={styles.navLinks}>
          {isAuthenticated && user ? (
            <div className={styles.userInfo}>
              <span className={styles.username}>{user.name}</span>
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
