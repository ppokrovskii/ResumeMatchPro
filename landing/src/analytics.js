// src/analytics.js
import ReactGA from 'react-ga4';

export const initGA = () => {
    const consent = localStorage.getItem('cookie-consent');
    // console.log('check', consent === 'accepted' && process.env.REACT_APP_GA_MEASUREMENT_ID);
    // if process.env.REACT_APP_GA_MEASUREMENT_ID variable is there then init reactga
    if (consent === 'accepted' && process.env.REACT_APP_GA_MEASUREMENT_ID) {
        ReactGA.initialize(process.env.REACT_APP_GA_MEASUREMENT_ID);
    } else {
        console.log('GA not initialized as no measurement id or user rejected cookies. consent:', consent);
    }
    //   if (process.env.NODE_ENV === 'prod') {
    //     ReactGA.initialize(process.env.REACT_APP_GA_MEASUREMENT_ID);
    //     console.log('GA initialized');
    //   } else
    //   {
    //     console.log('GA not initialized as not in prod');
    //   }

};

export const logPageView = () => {
    const consent = localStorage.getItem('cookie-consent');
    if (consent === 'accepted' && process.env.REACT_APP_ENV === 'prod') {
        ReactGA.send({ hitType: 'pageview', page: window.location.pathname + window.location.search });
    } else {
        console.log('GA page view not logged as not in prod or user rejected cookies. consent:', consent);
    }
};
