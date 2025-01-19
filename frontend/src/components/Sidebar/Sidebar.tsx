import PropTypes from 'prop-types';
import React, { useEffect, useRef } from 'react';
import Logo from '../Logo/Logo';
import styles from './Sidebar.module.css';

interface SidebarProps {
    sidebarOpen: boolean;
    setSidebarOpen: (open: boolean) => void;
    username: string;
    onSignOut: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ sidebarOpen, setSidebarOpen, username, onSignOut }) => {
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
                    <span>{username}</span>
                </li>
                <li className="semiBold font15 pointer">
                    <button onClick={onSignOut} className={styles.signOutButton}>Sign Out</button>
                </li>
            </ul>
        </nav>
    );
};

Sidebar.propTypes = {
    sidebarOpen: PropTypes.bool.isRequired,
    setSidebarOpen: PropTypes.func.isRequired,
    username: PropTypes.string.isRequired,
    onSignOut: PropTypes.func.isRequired,
};

export default Sidebar; 