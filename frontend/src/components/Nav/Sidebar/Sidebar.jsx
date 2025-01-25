import PropTypes from 'prop-types';
import { useContext } from 'react';
import { AuthContext } from '../../../contexts/AuthContext';
import styles from './Sidebar.module.css';

const Sidebar = ({ sidebarOpen, setSidebarOpen }) => {
    const { logout, user } = useContext(AuthContext);

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

Sidebar.propTypes = {
    sidebarOpen: PropTypes.bool.isRequired,
    setSidebarOpen: PropTypes.func.isRequired,
};

export default Sidebar; 