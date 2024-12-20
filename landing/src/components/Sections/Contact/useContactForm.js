import { useState } from 'react';
import { submitContactDetails } from "../../../services/contactService";

export const useContactForm = (handleOpenContactForm) => {
  const [formState, setFormState] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (field, value) => {
    setFormState(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccess(false);

    const contactDetails = {
      email: formState.email,
      phone: formState.phone,
      first_name: formState.firstName,
      last_name: formState.lastName,
    };

    try {
      const response = await submitContactDetails(contactDetails);
      if (response.ok) {
        setSuccess(true);
        setFormState({
          firstName: '',
          lastName: '',
          email: '',
          phone: ''
        });
        handleOpenContactForm('Contact details submitted successfully!');
      } else {
        setError('Failed to submit contact details.');
      }
    } catch (err) {
      setError('An error occurred while submitting contact details.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    formState,
    handleChange,
    handleSubmit,
    isSubmitting,
    error,
    success
  };
}; 