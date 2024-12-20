import React from "react";
import PropTypes from 'prop-types';
import styles from './Contact.module.css';
import ContactImg1 from "../../../assets/img/Professionals looking at a laptop_mj.png";
import ContactImg2 from "../../../assets/img/Rocket ship_mj.webp";
import ContactImg3 from "../../../assets/img/Finger pressing Join Now.webp";
import { useContactForm } from './useContactForm';

const FormField = ({ label, id, type = "text", value, onChange, required = true, autoComplete }) => (
  <>
    <label htmlFor={id} className={styles.label}>{label}:</label>
    <input
      type={type}
      id={id}
      name={id}
      value={value}
      onChange={onChange}
      required={required}
      autoComplete={autoComplete}
      className={styles.input}
    />
  </>
);

const ImageGallery = () => (
  <div className={styles.imagesContainer}>
    <div className={styles.imageColumn}>
      <div className={styles.contactImgBox}>
        <img src={ContactImg1} alt="Professionals looking at a laptop" className={styles.image} width="180" height="204" />
      </div>
      <div className={styles.contactImgBox}>
        <img src={ContactImg2} alt="Rocket ship" className={styles.image} width="180" height="295" />
      </div>
    </div>
    <div className={styles.imageColumn}>
      <div className={`${styles.contactImgBox} ${styles.offsetImage}`}>
        <img src={ContactImg3} alt="Finger pressing Join Now" className={styles.image} width="278" height="330" />
      </div>
    </div>
  </div>
);

const ContactForm = ({ onSubmit, formState, handleChange, isSubmitting }) => (
  <form 
    role="form"
    onSubmit={onSubmit} 
    autoComplete="on" 
    className={styles.form}
  >
    <FormField
      label="First Name"
      id="fname"
      value={formState.firstName}
      onChange={(e) => handleChange('firstName', e.target.value)}
      autoComplete="given-name"
    />
    
    <FormField
      label="Last Name"
      id="lname"
      value={formState.lastName}
      onChange={(e) => handleChange('lastName', e.target.value)}
      autoComplete="family-name"
    />
    
    <FormField
      label="Email"
      id="email"
      type="email"
      value={formState.email}
      onChange={(e) => handleChange('email', e.target.value)}
      autoComplete="email"
    />
    
    <FormField
      label="Phone Number"
      id="phone"
      type="tel"
      value={formState.phone}
      onChange={(e) => handleChange('phone', e.target.value)}
      required={false}
      autoComplete="tel"
    />
    
    <div className={styles.submitWrapper}>
      <button 
        type="submit" 
        disabled={isSubmitting} 
        className={styles.submitButton}
      >
        {isSubmitting ? 'Submitting...' : 'Get Early Access'}
      </button>
    </div>
  </form>
);

const Contact = ({ handleOpenContactForm }) => {
  const {
    formState,
    handleChange,
    handleSubmit,
    isSubmitting,
    error,
    success
  } = useContactForm();

  return (
    <section className={styles.wrapper} id="contact">
      <div className={styles.lightBg}>
        <div className={styles.container}>
          <div className={styles.headerInfo}>
            <h1 className={styles.title}>Signup for an early access</h1>
            <p className={styles.subtitle}>
              Get notified when beta testing starts. Receive updates on our latest features and services.
            </p>
          </div>
          
          <div className={styles.formWrapper}>
            <div className={styles.formContainer}>
              {success && <p className={styles.successMessage}>Contact details submitted successfully!</p>}
              {error && <p className={styles.errorMessage}>{error}</p>}
              
              <ContactForm
                onSubmit={handleSubmit}
                formState={formState}
                handleChange={handleChange}
                isSubmitting={isSubmitting}
              />
            </div>
            <ImageGallery />
          </div>
        </div>
      </div>
    </section>
  );
};

FormField.propTypes = {
  label: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  type: PropTypes.string,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  required: PropTypes.bool,
  autoComplete: PropTypes.string
};

ContactForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  formState: PropTypes.shape({
    firstName: PropTypes.string.isRequired,
    lastName: PropTypes.string.isRequired,
    email: PropTypes.string.isRequired,
    phone: PropTypes.string.isRequired
  }).isRequired,
  handleChange: PropTypes.func.isRequired,
  isSubmitting: PropTypes.bool.isRequired
};

Contact.propTypes = {
  handleOpenContactForm: PropTypes.func.isRequired
};

export default Contact; 