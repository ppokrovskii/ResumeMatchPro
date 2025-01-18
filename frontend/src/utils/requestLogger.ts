/* eslint-disable no-console */
import { LogLevel } from '@azure/msal-browser';

const isDevEnvironment = process.env.NODE_ENV === 'development';

// MSAL logging configuration
export const msalLoggerConfig = {
    loggerOptions: {
        loggerCallback: (level: LogLevel, message: string, containsPii: boolean) => {
            if (containsPii) {
                console.log(`🔒 MSAL (contains PII) - ${LogLevel[level]}: ${message}`);
            } else {
                console.log(`🔑 MSAL - ${LogLevel[level]}: ${message}`);
            }
        },
        logLevel: LogLevel.Verbose,
        piiLoggingEnabled: true
    }
};

// MSAL specific logging
export const enableMsalLogging = () => {
    if (isDevEnvironment) {
        const msalEvents = [
            'msal:loginStart',
            'msal:loginSuccess',
            'msal:loginFailure',
            'msal:acquireTokenStart',
            'msal:acquireTokenSuccess',
            'msal:acquireTokenFailure',
            'msal:ssoSilent',
            'msal:handleRedirectStart',
            'msal:handleRedirectEnd'
        ];

        msalEvents.forEach(eventName => {
            window.addEventListener(eventName, (event) => {
                console.log(`🔐 MSAL Event - ${eventName}:`, event);
            });
        });
    }
}; 