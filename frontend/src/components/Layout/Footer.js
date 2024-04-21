// Footer.js

import React from 'react';

const Footer = () => {
    return (
        <footer style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '1rem', backgroundColor: '#f5f5f5', marginTop: 'auto' }}>
            <p style={{ margin: 0 }}>
                © {new Date().getFullYear()} MyReactApp. All rights reserved.
            </p>
            {/* Optionally, add more links or information here */}
        </footer>
    );
};

export default Footer;
