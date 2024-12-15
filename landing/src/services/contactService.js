const getApiUrl = () => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL;
    const env = process.env.REACT_APP_ENV;
    console.log(`Running in ${env} environment with backend URL: ${backendUrl}`);
    return backendUrl;
};

export const submitContactDetails = async (contactDetails) => {
    const backendUrl = getApiUrl();
    try {
        const response = await fetch(`${backendUrl}/contact_details`, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify(contactDetails),
        });
        return response;
        } catch (error) {
            console.error('Error submitting contact details:', error);
        }
    }
