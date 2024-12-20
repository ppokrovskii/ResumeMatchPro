import { useState } from 'react';
import { submitContactDetails } from '../services/contactService';

export const useContactForm = () => {
  const [isContactFormOpen, setIsContactFormOpen] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');

  const handleOpenContactForm = () => {
    setIsContactFormOpen(true);
  };

  const handleCloseContactForm = () => {
    setIsContactFormOpen(false);
  };

  const handleSuccessSubmitContactDetails = async (message) => {
    try {
      const response = await submitContactDetails({
        email: message.email,
        phone: message.phone,
        first_name: message.first_name,
        last_name: message.last_name
      });
      if (response.ok) {
        setNotificationMessage('Contact details submitted successfully!');
      } else {
        setNotificationMessage('Failed to submit contact details.');
      }
    } catch (error) {
      setNotificationMessage('An error occurred while submitting contact details.');
    } finally {
      handleCloseContactForm();
    }
  };

  const handleNotificationClose = () => {
    setNotificationMessage('');
  };

  return {
    isContactFormOpen,
    notificationMessage,
    handleOpenContactForm,
    handleCloseContactForm,
    handleSuccessSubmitContactDetails,
    handleNotificationClose
  };
}; 