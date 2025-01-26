import { useMsal } from '@azure/msal-react';
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import BurgerIcon from '../../../assets/svg/BurgerIcon';
import { registerUser, useAuth } from '../../../contexts/AuthContext';
import commonStyles from '../../../styles/common.module.css';
import { DebugInfo } from '../../DebugInfo/DebugInfo';
import Logo from '../../Logo/Logo';
import Sidebar from '../Sidebar/Sidebar';
import styles from './TopNavbar.module.css';

const TopNavbar: React.FC = () => {
    const { isAuthenticated, user, logout } = useAuth();
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const { instance } = useMsal();

    const handleCreateUser = async () => {
        if (!user?.account || !user?.idTokenClaims) return;
        try {
            await registerUser(user.idTokenClaims, user.account, instance);
        } catch (error) {
            console.error('Failed to create user:', error);
        }
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
                            <button
                                className={commonStyles.primaryButton}
                                onClick={handleCreateUser}
                                style={{ marginRight: '8px' }}
                            >
                                Create User
                            </button>
                            <button onClick={logout} className={commonStyles.primaryButton}>Sign Out</button>
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