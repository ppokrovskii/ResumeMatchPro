// File: src/app/App.tsx

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// import AboutPage from '../pages/AboutPage';
// import LoginRegistrationPage from '../pages/LoginRegistrationPage';
// import UserProfilePage from '../pages/UserProfilePage';
// import ResultDetailsPage from '../pages/ResultDetailsPage';
import './App.css'; // Optional: global styles
import HomePage from './pages/Homeage/HomePage';
import Header from './components/Header/Header';
import Footer from './components/Footer/Footer';

const App = () => {
  return (
    <Router>
      <div className="app">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            {/* <Route path="/about" element={<AboutPage />} /> */}
            {/* <Route path="/login" element={<LoginRegistrationPage />} /> */}
            {/* <Route path="/profile" element={<UserProfilePage />} /> */}
            {/* <Route path="/results/:fileId" element={<ResultDetailsPage />} /> */}
            {/* Additional routes can be added here */}
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
};

export default App;
