describe('Authentication', () => {
    let redirectCount = 0;
    const MAX_REDIRECTS = 5;

    beforeEach(() => {
        redirectCount = 0;

        // Set up logging for all requests
        cy.intercept('**', (req) => {
            console.log(`[Request] ${req.method} ${req.url}`);
            req.continue((res) => {
                if (res.statusCode === 301 || res.statusCode === 302 || res.statusCode === 303 || res.statusCode === 307) {
                    console.log(`[Redirect] Status: ${res.statusCode}, Location: ${res.headers['location']}`);
                    console.log(`[Headers] ${JSON.stringify(res.headers, null, 2)}`);
                } else {
                    console.log(`[Response] Status: ${res.statusCode}`);
                }
            });
        });

        // Set up auth request interception
        cy.intercept('GET', '**/oauth2/v2.0/authorize*', (req) => {
            const url = new URL(req.url);
            console.log('[Auth] Intercepting auth request to modify scope');
            console.log(`[Auth] Original scope: ${url.searchParams.get('scope')}`);
            url.searchParams.set('scope', 'openid profile');
            req.url = url.toString();
            console.log(`[Auth] Modified URL: ${req.url}`);
        }).as('authRequest');

        // Set up URL change monitoring
        cy.on('url:changed', (url) => {
            redirectCount++;
            console.log(`[Navigation] URL changed to: ${url} (redirect #${redirectCount})`);

            if (redirectCount > MAX_REDIRECTS) {
                throw new Error(`Too many redirects (${MAX_REDIRECTS}). Stopping test.`);
            }

            if (url.includes('error=')) {
                const errorParams = new URLSearchParams(url.split('#')[1]);
                console.log(`[Error] Type: ${errorParams.get('error')}`);
                console.log(`[Error] Description: ${errorParams.get('error_description')}`);
                throw new Error(`Authentication error: ${errorParams.get('error_description')}`);
            }
        });

        cy.visit('http://localhost:3000');
    });

    it('should redirect to login when not authenticated', () => {
        cy.wait('@authRequest', { timeout: 10000 }).then((interception) => {
            console.log('\n=== Auth Request Details ===');
            console.log(`[Auth] Method: ${interception.request.method}`);
            console.log(`[Auth] URL: ${interception.request.url}`);
            console.log(`[Auth] Headers: ${JSON.stringify(interception.request.headers, null, 2)}`);

            const url = new URL(interception.request.url);
            console.log('\n=== Auth Parameters ===');
            url.searchParams.forEach((value, key) => {
                console.log(`[Param] ${key}: ${value}`);
            });
        });

        cy.url().should('not.include', 'error=', { timeout: 10000 });
    });

    it('should handle auth callback correctly', () => {
        cy.intercept('GET', '**/auth-callback/**', (req) => {
            console.log(`[Callback] URL: ${req.url}`);
        }).as('authCallback');

        cy.visit('http://localhost:3000/auth-callback/');
        cy.wait('@authCallback', { timeout: 10000 });
        cy.url().should('not.include', 'error=', { timeout: 10000 });
    });
}); 