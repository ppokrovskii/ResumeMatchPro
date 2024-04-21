// httpClient.js

/**
 * Helper function to get the stored auth token from local storage.
 */
const getAuthToken = () => {
    const user = JSON.parse(localStorage.getItem('user'));
    return user?.token;
};

/**
 * Generic fetch wrapper to include headers and error handling.
 * @param {string} url The full URL to the resource.
 * @param {Object} [options={}] The options for the fetch request.
 * @returns {Promise<any>} The response from the fetch request.
 */
const httpClient = async (url, options = {}) => {
    // Default headers
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers, // Allows overriding and adding headers
    };

    // Include the Authorization header with the JWT if available
    const token = getAuthToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers,
        });

        // Check if the response was successful
        if (!response.ok) {
            const error = new Error('An error occurred while fetching the data.');
            // Attach additional info to the error object
            error.info = await response.json();
            error.status = response.status;
            throw error;
        }

        // Attempt to parse the response body as JSON
        return response.json();
    } catch (error) {
        console.error("HTTP Client Error:", error);
        throw error;
    }
};

export default httpClient;
