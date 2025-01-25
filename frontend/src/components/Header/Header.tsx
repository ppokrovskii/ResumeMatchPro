// File: src/components/Header/Header.tsx

import React, { useContext, useEffect, useState } from 'react';
import BurgerIcon from '../../assets/svg/BurgerIcon';
import { AuthContext } from '../../contexts/AuthContext';
import Logo from '../Logo/Logo';
import Sidebar from '../Sidebar/Sidebar';
import styles from './Header.module.css';

const Header: React.FC = () => {
  const { isAuthenticated, user, logout } = useContext(AuthContext);
  const [y, setY] = useState(window.scrollY);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setY(window.scrollY);
    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [y]);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
      />
      <header
        className={styles.wrapper}
        style={y > 100 ? { height: "60px" } : { height: "80px" }}
      >
        <div className={styles.navInner}>
          <Logo />
          <div className={styles.navLinks}>
            <div className={styles.userInfo}>
              <span className={styles.username}>{user?.name}</span>
              <button onClick={logout} className={styles.button}>Sign Out</button>
            </div>
          </div>
          <button
            className={styles.burgerWrapper}
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <BurgerIcon />
          </button>
        </div>
      </header>
    </>
  );
};

export default Header;
