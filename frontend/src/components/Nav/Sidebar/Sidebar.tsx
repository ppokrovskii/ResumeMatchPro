import React, { useState } from 'react';
import { useAuth } from '../../../contexts/AuthContext';
import { UserInfoModal } from '../../UserInfoModal/UserInfoModal';
import styles from './Sidebar.module.css';

interface SidebarProps {
    sidebarOpen: boolean;
    setSidebarOpen: (open: boolean) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ sidebarOpen, setSidebarOpen }) => {
    const { logout, user } = useAuth();
    const [userInfoModalOpen, setUserInfoModalOpen] = useState(false);

    return (
        <>
            <UserInfoModal
                isOpen={userInfoModalOpen}
                onClose={() => setUserInfoModalOpen(false)}
            />
            <nav className={styles.wrapper} data-open={sidebarOpen}>
                <div className={styles.userInfo}>
                    <button
                        className={styles.usernameButton}
                        onClick={() => setUserInfoModalOpen(true)}
                    >
                        {user?.name}
                    </button>
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
        </>
    );
};

export default Sidebar; 