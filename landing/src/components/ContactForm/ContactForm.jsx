// src/components/ContactForm.js
import React, { useState } from 'react';
import PropTypes from 'prop-types';
import styles from './ContactForm.module.css';
import { submitContactDetails } from '../../services/contactService';

const ContactForm = ({ isOpen, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState('');

  const validateForm = () => {
    const newErrors = {};
    if (!formData.first_name) newErrors.first_name = 'First name is required';
    if (!formData.last_name) newErrors.last_name = 'Last name is required';
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(formData.email)) {
      newErrors.email = 'Invalid email address';
    }
    if (!formData.phone) {
      newErrors.phone = 'Phone number is required';
    } else if (!/^\d{10,}$/.test(formData.phone.replace(/\D/g, ''))) {
      newErrors.phone = 'Invalid phone number';
    }
    return newErrors;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = validateForm();
    
    setFormError('');
    
    if (Object.keys(newErrors).length === 0) {
      setIsSubmitting(true);
      try {
        onSuccess({
          email: formData.email,
          phone: formData.phone,
          first_name: formData.first_name,
          last_name: formData.last_name
        });
        setFormData({ first_name: '', last_name: '', email: '', phone: '' });
      } catch (error) {
        console.error('Error submitting form:', error);
        setFormError(
          error.message === 'Failed to submit'
            ? 'Failed to submit the form.'
            : 'An unexpected error occurred.'
        );
      } finally {
        setIsSubmitting(false);
      }
    } else {
      setErrors(newErrors);
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
        <button 
          className={styles.closeButton} 
          onClick={onClose}
          aria-label="Close form"
        >
          ×
        </button>

        <form className={styles.form} onSubmit={handleSubmit}>
          <h2>Get Early Access</h2>
          
          {formError && (
            <div className={styles.formError}>
              {formError}
            </div>
          )}

          <div className={styles.inputGroup}>
            <label className={styles.label} htmlFor="first_name">First Name</label>
            <input
              id="first_name"
              name="first_name"
              className={styles.input}
              value={formData.first_name}
              onChange={handleChange}
            />
            {errors.first_name && <span className={styles.error}>{errors.first_name}</span>}
          </div>

          <div className={styles.inputGroup}>
            <label className={styles.label} htmlFor="last_name">Last Name</label>
            <input
              id="last_name"
              name="last_name"
              className={styles.input}
              value={formData.last_name}
              onChange={handleChange}
            />
            {errors.last_name && <span className={styles.error}>{errors.last_name}</span>}
          </div>

          <div className={styles.inputGroup}>
            <label className={styles.label} htmlFor="email">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              className={styles.input}
              value={formData.email}
              onChange={handleChange}
            />
            {errors.email && <span className={styles.error}>{errors.email}</span>}
          </div>

          <div className={styles.inputGroup}>
            <label className={styles.label} htmlFor="phone">Phone Number</label>
            <input
              id="phone"
              name="phone"
              type="tel"
              className={styles.input}
              value={formData.phone}
              onChange={handleChange}
              placeholder="e.g., 0581234567"
            />
            {errors.phone && <span className={styles.error}>{errors.phone}</span>}
          </div>

          <div className={styles.buttonHolder}>
            <button 
              type="submit" 
              className={styles.submitButton}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Submit'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

ContactForm.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired,
};

export default ContactForm;
