import React, { useEffect, useState } from 'react';
import styles from './CookieConsent.module.css';
import FullButton from '../Buttons/FullButton';

const CookieConsent = ({initGA}) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem('cookie-consent');
    if (!consent) {
      setVisible(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('cookie-consent', 'accepted');
    setVisible(false);
    initGA();
  };

  const handleReject = () => {
    localStorage.setItem('cookie-consent', 'rejected');
    setVisible(false);
  };

  return (
    visible && (
      <div className={styles.modal}>
        <div className={styles.modalContent}>
          <h2>Cookie Consent</h2>
          <p>We use cookies to improve your experience. Do you accept our cookie policy?</p>
          <div className={styles.buttonContainer}>
            <FullButton title='Reject' action={handleReject} border='solid #580cd2 1px' backgroundColor='#fff' color='#580cd2'/>
            <FullButton title='Accept' action={handleAccept} />
          </div>
        </div>
      </div>
    )
  );
};

export default CookieConsent;
