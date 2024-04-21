// authService.js

const API_URL = 'YOUR_BACKEND_API_URL'; // Change this to your FastAPI backend URL

/**
 * Send token to backend for validation and login
 * @param {string} token - The token received from Azure authentication.
 */
const login = async (token) => {
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
        });
        if (!response.ok) {
            throw new Error('Login failed');
        }
        const data = await response.json();
        // Assuming the backend responds with a token or user data to be stored in localStorage
        localStorage.setItem('user', JSON.stringify(data));
    } catch (error) {
        console.error('An error occurred during login:', error);
        throw error;
    }
};

/**
 * Logout the user
 */
const logout = () => {
    // Remove user data from localStorage
    localStorage.removeItem('user');
    // Optionally, redirect the user to the Azure logout URL or your custom logout route
};

export default {
    login,
    logout,
};
