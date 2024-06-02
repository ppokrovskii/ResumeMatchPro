// src/components/ContactForm.js
import React, { useState } from 'react';
import { submitContactDetails } from '../../services/contactService';
import './ContactForm.css';
import FullButton from '../Buttons/FullButton';

const ContactForm = ({ isOpen, onClose, onSuccess }) => {
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState(''); // added phone
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccess(false);

    const contactDetails = {
      email,
      phone,
      first_name: firstName,
      last_name: lastName,
    };

    try {
      const response = await submitContactDetails(contactDetails);
      if (response.ok) {
        setSuccess(true);
        setEmail('');
        setFirstName('');
        setLastName('');
        // onClose();
        debugger;
        onSuccess('Contact details submitted successfully!')
      } else {
        setError('Failed to submit contact details.');
      }
    } catch (err) {
      setError('An error occurred while submitting contact details.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="popup-form">
      <div className="popup-form-content">
        <button className="close-button" onClick={onClose}>×</button>
        <h2>Get notified when beta testing starts</h2>
        {success && <p>Contact details submitted successfully!</p>}
        {error && <p class='redColor'>{error}</p>}
        <form onSubmit={handleSubmit}>
          <div>
            <label>Email</label>
            <input type="email" name="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          {/* phone */}
          <div>
            <label>phone number</label>
            <input type="text" value={phone} onChange={(e) => setPhone(e.target.value)} />
          </div>
          <div>
            <label>First Name</label>
            <input type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)} required />
          </div>
          <div>
            <label>Last Name</label>
            <input type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} required />
          </div>
          {/* align center */}
          <div class="buttonHolder">
            <button type="submit" disabled={isSubmitting} class='submit-button'>
              {isSubmitting ? 'Submitting...' : 'Submit'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ContactForm;
