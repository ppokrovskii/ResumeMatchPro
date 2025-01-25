import { useContext, useState } from 'react';
import BurgerIcon from '../../../assets/svg/BurgerIcon';
import { AuthContext } from '../../../contexts/AuthContext';
import Logo from '../../Logo/Logo';
import Sidebar from '../Sidebar/Sidebar';
import styles from './TopNavbar.module.css';

const TopNavbar = () => {
    const { isAuthenticated, user, logout } = useContext(AuthContext);
    const [sidebarOpen, setSidebarOpen] = useState(false);

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
                            <button onClick={logout} className={styles.button}>Sign Out</button>
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