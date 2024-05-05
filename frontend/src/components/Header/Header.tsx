// File: src/components/Header/Header.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import { HomeOutlined, InfoCircleOutlined, UserOutlined } from '@ant-design/icons';
import 'antd/dist/reset.css';
import styles from './Header.module.css';

const Header: React.FC = () => {
  return (
    <header className={styles.appHeader}>
      <div className={styles.headerLogo}>
        {/* header text Resume Match Pro */}
        <Link to="/">Resume Match Pro</Link>
      </div>
      <nav className={styles.headerNav}>
        <ul>
          <li><Link to="/">Home</Link></li>
          <li><Link to="/about">About</Link></li>
          <li><Link to="/login">Login</Link></li>
        </ul>
      </nav>
      <div className={styles.headerUser}>
        <UserOutlined />
        <span> My Profile</span>
      </div>
    </header>
  );
};

export default Header;
