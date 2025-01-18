import { defineConfig } from 'cypress';

export default defineConfig({
    e2e: {
        setupNodeEvents(on, config) {
            // Add task for logging
            on('task', {
                log(message) {
                    console.log(message);
                    return null;
                }
            });
        },
        baseUrl: 'http://localhost:3000',
        defaultCommandTimeout: 10000,
        video: true,
        screenshotOnRunFailure: true,
        chromeWebSecurity: false,
        env: {
            DEBUG: 'cypress:server:request*'
        }
    },
    env: {
        FRONTEND_CLIENT_ID: process.env.REACT_APP_FRONTEND_CLIENT_ID || '42517ab6-e124-413b-8e1f-ba4d38e13c9c',
    },
}); 