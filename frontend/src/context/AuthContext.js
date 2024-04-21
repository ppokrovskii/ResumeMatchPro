import React, { createContext, useContext, useState, useEffect } from 'react';

// Create the context
const AuthContext = createContext();

// Hook for child components to get the auth object
// and re-render when it changes.
export const useAuth = () => {
    return useContext(AuthContext);
};

// Provider component that wraps your app and makes auth object
// available to any child component that calls `useAuth()`.
export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check for token in local storage to maintain session
        const user = JSON.parse(localStorage.getItem('user'));
        if (user) {
            setUser(user);
        }
        setLoading(false);
    }, []);

    // Sign in
    const login = async (email, password) => {
        try {
            // Here, integrate with your backend authentication
            // For demonstration, we assume a successful login
            const token = 'fakeToken'; // This should come from your backend upon successful authentication
            const user = { email, token };

            // Persist user's authentication in local storage
            localStorage.setItem('user', JSON.stringify(user));
            setUser(user);
        } catch (error) {
            console.error("Login failed:", error);
            throw error; // Throw error to be caught by login form for potential error messaging
        }
    };

    // Sign out
    const logout = () => {
        localStorage.removeItem('user');
        setUser(null);
    };

    const value = {
        user,
        login,
        logout,
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
