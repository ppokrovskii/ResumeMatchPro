// src/components/Notification.js
import React, { useEffect, useState } from 'react';
import './Notification.css';

const Notification = ({ message, onClose }) => {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(() => {
        onClose();
      }, 500); // Duration of the hide animation
    }, 5000); // 5 seconds

    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className={`notification ${visible ? 'show' : 'hide'}`} onClick={onClose}>
      {message}
    </div>
  );
};

export default Notification;
