// LogoutButton.js

import React from 'react';
import {useAuth} from '../../context/AuthContext'; // Adjust the import path as necessary
import {useNavigate} from 'react-router-dom';

const LogoutButton = () => {
    const {logout} = useAuth(); // Access logout method from AuthContext
    const navigate = useNavigate();

    const handleLogout = () => {
        logout(); // Execute logout method
        navigate('/login'); // Redirect to login page after logout
    };

    return (
        <button onClick={handleLogout} style={{cursor: 'pointer'}}>
            Log Out
        </button>
    );
};

export default LogoutButton;
