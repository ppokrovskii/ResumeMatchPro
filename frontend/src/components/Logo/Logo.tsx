import React from 'react';
import { Link } from 'react-router-dom';
import styles from './Logo.module.css';

interface LogoProps {
    className?: string;
}

const Logo: React.FC<LogoProps> = ({ className }) => {
    return (
        <Link to="/" className={`${styles.logo} ${className || ''}`}>
            ResumeMatchPro
        </Link>
    );
};

export default Logo; 