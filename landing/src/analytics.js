// src/analytics.js
import ReactGA from 'react-ga4';

export const initGA = () => {
    const env = process.env.REACT_APP_ENV;
    const measurementId = process.env.REACT_APP_GA_MEASUREMENT_ID;
    
    if (env === 'prod' && measurementId) {
        // Initialize GA only in production
        ReactGA.initialize(measurementId);
        console.log('GA initialized in production');
    } else {
        console.log('GA not initialized in development');
    }
};

export const logPageView = () => {
    const consent = localStorage.getItem('cookie-consent');
    if (consent === 'accepted' && process.env.REACT_APP_ENV === 'prod') {
        ReactGA.send({ hitType: 'pageview', page: window.location.pathname + window.location.search });
    } else {
        console.log('GA page view not logged as not in prod or user rejected cookies. consent:', consent);
    }
};
