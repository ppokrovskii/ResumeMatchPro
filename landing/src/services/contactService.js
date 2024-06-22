  export const submitContactDetails = async (contactDetails) => {
    const backendUrl = process.env.LANDING_REACT_APP_BACKEND_URL;
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
