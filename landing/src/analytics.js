// src/analytics.js
import ReactGA from 'react-ga4';

export const initGA = () => {
    // if process.env.REACT_APP_GA_MEASUREMENT_ID variable is there then init reactga
    if (process.env.REACT_APP_GA_MEASUREMENT_ID) {
        ReactGA.initialize(process.env.REACT_APP_GA_MEASUREMENT_ID);
        console.log('GA initialized');
    } else {
        console.log('GA not initialized as no measurement id');
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
    if (process.env.NODE_ENV === 'prod') {
        ReactGA.send({ hitType: 'pageview', page: window.location.pathname + window.location.search });
    }
};
