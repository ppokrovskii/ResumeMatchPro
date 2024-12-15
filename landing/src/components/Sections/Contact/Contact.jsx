import React, { useState } from "react";
import styles from './Contact.module.css';
import ContactImg1 from "../../../assets/img/Professionals looking at a laptop_mj.png";
import ContactImg2 from "../../../assets/img/Rocket ship_mj.webp";
import ContactImg3 from "../../../assets/img/Finger pressing Join Now.webp";
import { submitContactDetails } from "../../../services/contactService";

export default function Contact({ handleOpenContactForm }) {
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
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
        setPhone('');
        setFirstName('');
        setLastName('');
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
            <form onSubmit={handleSubmit} autoComplete="on" className={styles.form}>
              {success && <p className={styles.successMessage}>Contact details submitted successfully!</p>}
              {error && <p className={styles.errorMessage}>{error}</p>}
              
              <label className={styles.label}>First Name:</label>
              <input
                type="text"
                id="fname"
                name="fname"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                required
                autoComplete="given-name"
                className={styles.input}
              />
              
              <label className={styles.label}>Last Name:</label>
              <input
                type="text"
                id="lname"
                name="lname"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                required
                autoComplete="family-name"
                className={styles.input}
              />
              
              <label className={styles.label}>Email:</label>
              <input
                type="email"
                id="email"
                name="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                className={styles.input}
              />
              
              <label className={styles.label}>Phone Number:</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                autoComplete="tel"
                className={styles.input}
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

            <div className={styles.imagesContainer}>
              <div className={styles.imageColumn}>
                <div className={styles.contactImgBox}>
                  <img src={ContactImg1} alt="office" className={styles.image} width="180" height="204" />
                </div>
                <div className={styles.contactImgBox}>
                  <img src={ContactImg2} alt="office" className={styles.image} width="180" height="295" />
                </div>
              </div>
              <div className={styles.imageColumn}>
                <div className={`${styles.contactImgBox} ${styles.offsetImage}`}>
                  <img src={ContactImg3} alt="office" className={styles.image} width="278" height="330" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
} 