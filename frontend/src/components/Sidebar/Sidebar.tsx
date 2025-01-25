import PropTypes from 'prop-types';
import React, { useContext, useEffect, useRef } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import Logo from '../Logo/Logo';
import styles from './Sidebar.module.css';

interface SidebarProps {
    sidebarOpen: boolean;
    setSidebarOpen: (open: boolean) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ sidebarOpen, setSidebarOpen }) => {
    const { isAuthenticated, user, logout } = useContext(AuthContext);
    const sidebarRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (sidebarRef.current && !sidebarRef.current.contains(event.target as Node)) {
                setSidebarOpen(false);
            }
        };

        if (sidebarOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        } else {
            document.removeEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [sidebarOpen, setSidebarOpen]);

    if (!isAuthenticated) {
        return null;
    }

    return (
        <nav ref={sidebarRef} className={`${styles.wrapper} animate whiteBg`} data-open={sidebarOpen}>
            <div className={`${styles.sidebarHeader} flexSpaceBetween`}>
                <Logo />
                <button
                    onClick={() => setSidebarOpen(false)}
                    className={`${styles.closeBtn} animate pointer`}
                >
                    &times;
                </button>
            </div>

            <ul className={`${styles.ulStyle} flexNullCenter flexColumn`}>
                <li className="semiBold font15 pointer">
                    <span>{user?.name}</span>
                </li>
                <li className="semiBold font15 pointer">
                    <button onClick={logout} className={styles.signOutButton}>Sign Out</button>
                </li>
            </ul>
        </nav>
    );
};

Sidebar.propTypes = {
    sidebarOpen: PropTypes.bool.isRequired,
    setSidebarOpen: PropTypes.func.isRequired,
};

export default Sidebar; 