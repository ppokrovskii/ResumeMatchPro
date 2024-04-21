// Header.js

import React from 'react';
import {Link, useNavigate} from 'react-router-dom';
import {useAuth} from '../../context/AuthContext'; // Adjust the import path as necessary
import LogoutButton from '../Auth/LogoutButton'; // Adjust the import path as necessary

const Header = () => {
    const {user} = useAuth();
    const navigate = useNavigate();

    return (
        <header style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '1rem',
            backgroundColor: '#f0f0f0'
        }}>
            <h1><Link to="/" style={{textDecoration: 'none', color: 'black'}}>MyApp</Link></h1>
            <nav>
                <ul style={{listStyle: 'none', display: 'flex', gap: '20px', margin: 0, padding: 0}}>
                    <li><Link to="/about" style={{textDecoration: 'none', color: 'black'}}>About</Link></li>
                    {user ? (
                        <>
                            <li><Link to="/home" style={{textDecoration: 'none', color: 'black'}}>Home</Link></li>
                            <li><LogoutButton/></li>
                        </>
                    ) : (
                        <>
                            <li><Link to="/login" style={{textDecoration: 'none', color: 'black'}}>Login</Link></li>
                            {/* If you have a signup page, include it here */}
                        </>
                    )}
                </ul>
            </nav>
        </header>
    );
};

export default Header;
