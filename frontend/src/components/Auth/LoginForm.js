// LoginForm.js

import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext'; // Adjust the import path as necessary
import { useNavigate } from 'react-router-dom';

const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login } = useAuth(); // Use the login function from AuthContext
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        try {
            await login(email, password);
            navigate('/home'); // Redirect to the home page upon successful login
        } catch (error) {
            alert('Failed to log in'); // Replace with a more user-friendly error handling
        }
    };

    return (
        <form onSubmit={handleSubmit} style={{ maxWidth: '320px', margin: 'auto' }}>
            <div style={{ marginBottom: '20px' }}>
                <label htmlFor="email" style={{ display: 'block', marginBottom: '5px' }}>Email</label>
                <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    style={{ width: '100%', padding: '8px' }}
                />
            </div>
            <div style={{ marginBottom: '20px' }}>
                <label htmlFor="password" style={{ display: 'block', marginBottom: '5px' }}>Password</label>
                <input
                    type="password"
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    style={{ width: '100%', padding: '8px' }}
                />
            </div>
            <button type="submit" style={{ width: '100%', padding: '10px', cursor: 'pointer' }}>
                Log In
            </button>
        </form>
    );
};

export default LoginForm;
