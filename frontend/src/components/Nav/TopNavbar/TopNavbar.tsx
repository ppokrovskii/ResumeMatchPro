import { useMsal } from '@azure/msal-react';
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import BurgerIcon from '../../../assets/svg/BurgerIcon';
import { useAuth } from '../../../contexts/AuthContext';
import commonStyles from '../../../styles/common.module.css';
import { DebugInfo } from '../../DebugInfo/DebugInfo';
import Logo from '../../Logo/Logo';
import Sidebar from '../Sidebar/Sidebar';
import styles from './TopNavbar.module.css';

const TopNavbar: React.FC = () => {
    const { isAuthenticated, user } = useAuth();
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const { instance } = useMsal();

    const handleSignOut = () => {
        instance.logoutRedirect();
    };

    if (!isAuthenticated) {
        return null;
    }

    return (
        <>
            <Sidebar
                sidebarOpen={sidebarOpen}
                setSidebarOpen={setSidebarOpen}
            />
            <header className={styles.wrapper}>
                <div className={styles.navInner}>
                    <Logo />
                    <div className={styles.navLinks}>
                        <div className={styles.userInfo}>
                            <span className={styles.username}>{user?.name}</span>
                            <DebugInfo claims={user} />
                            {user?.idTokenClaims?.extension_IsAdmin && (
                                <Link to="/admin" className={commonStyles.primaryButton}>Admin</Link>
                            )}
                            <button onClick={handleSignOut} className={commonStyles.primaryButton}>Sign Out</button>
                        </div>
                    </div>
                    <button
                        className={styles.burgerWrapper}
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                    >
                        {sidebarOpen ? '×' : <BurgerIcon />}
                    </button>
                </div>
            </header>
        </>
    );
};

export default TopNavbar; 