// ***********************************************************
// This example support/e2e.ts is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

declare global {
    namespace Cypress {
        interface Chainable {
            // Add custom commands here
        }
    }
}

// Import commands.js using ES2015 syntax:
import './commands';

Cypress.on('uncaught:exception', (err) => {
    // Returning false here prevents Cypress from failing the test
    // This is useful for handling MSAL auth errors that we expect during testing
    return false;
}); 