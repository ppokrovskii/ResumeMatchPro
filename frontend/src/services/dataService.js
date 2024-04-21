// dataService.js

const API_URL = 'YOUR_BACKEND_API_ENDPOINT'; // e.g., 'http://localhost:8000/api'

/**
 * Helper function to get the stored auth token from local storage.
 */
const getAuthToken = () => {
    const user = JSON.parse(localStorage.getItem('user'));
    return user?.token;
};

/**
 * Fetches data from a specified endpoint in the FastAPI backend.
 * @param {string} endpoint - The endpoint to fetch data from, appended to the API_URL.
 * @returns {Promise<any>} The data from the backend.
 */
const fetchData = async (endpoint) => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('No auth token found. Please login.');
    }

    try {
        const response = await fetch(`${API_URL}/${endpoint}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        return response.json();
    } catch (error) {
        console.error("Failed to fetch data:", error);
        throw error;
    }
};

export default {
    fetchData,
};
