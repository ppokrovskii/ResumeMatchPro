import React from 'react';
import { Route, Routes } from 'react-router-dom';
import AuthenticationTemplate from './components/auth/AuthenticationTemplate';
import AuthCallback from './components/AuthCallback/AuthCallback';
import HomePage from './pages/Homeage/HomePage';

const AppRoutes: React.FC = () => {
    const handleAuthenticated = (user: { name: string; isAdmin: boolean }) => {
        // Authentication successful
    };

    return (
        <Routes>
            <Route path="/auth-callback" element={<AuthCallback />} />
            <Route
                path="/"
                element={
                    <AuthenticationTemplate onAuthenticated={handleAuthenticated}>
                        <HomePage />
                    </AuthenticationTemplate>
                }
            />
        </Routes>
    );
};

export default AppRoutes; 