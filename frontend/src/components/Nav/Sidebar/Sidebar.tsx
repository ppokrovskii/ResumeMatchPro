import React from 'react';
import { useAuth } from '../../../contexts/AuthContext';
import styles from './Sidebar.module.css';

interface SidebarProps {
    sidebarOpen: boolean;
    setSidebarOpen: (open: boolean) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ sidebarOpen, setSidebarOpen }) => {
    const { logout, user } = useAuth();

    return (
        <nav className={styles.wrapper} data-open={sidebarOpen}>
            <div className={styles.userInfo}>
                <span className={styles.username}>{user?.name}</span>
            </div>
            <ul className={styles.ulStyle}>
                <li>
                    <button
                        onClick={() => {
                            setSidebarOpen(false);
                            logout();
                        }}
                        className={styles.signOutButton}
                    >
                        Sign Out
                    </button>
                </li>
            </ul>
        </nav>
    );
};

export default Sidebar; 