import React from 'react';
import {BrowserRouter as Router, Routes, Route, Navigate} from 'react-router-dom';
import {AuthProvider, useAuth} from './context/AuthContext';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import LoginForm from './components/Auth/LoginForm';
import Header from './components/Layout/Header';
import Footer from './components/Layout/Footer';

// Adjusted RequireAuth component for private routes
const RequireAuth = ({children}) => {
    const {isAuthenticated} = useAuth();
    return isAuthenticated ? children : <Navigate to="/login" replace/>;
};

const App = () => {
    return (
        <AuthProvider>
            <Router>
                <div className="app">
                    <Header/>
                    <main style={{padding: '1rem'}}>
                        <Routes>
                            <Route path="/login" element={<LoginForm/>}/>
                            <Route path="/about" element={<AboutPage/>}/>
                            {/*/!* Apply RequireAuth to protect the HomePage route *!/*/}
                            <Route path="/home" element={<RequireAuth><HomePage/></RequireAuth>}/>
                            <Route path="/" element={<Navigate replace to="/about"/>}/>
                            {/* Default fallback to About Page */}
                            <Route path="*" element={<Navigate replace to="/about"/>}/>
                        </Routes>
                    </main>
                    <Footer/>
                </div>
            </Router>
        </AuthProvider>
    );
};

export default App;
