import React, { useState } from 'react';
import styles from './HowItWorks.module.css';
import ProjectImg1 from '../../../assets/img/projects/rmp_design1.png';
import ProjectImg2 from '../../../assets/img/projects/rmp_design2.png';
import ProjectImg3 from '../../../assets/img/projects/rmp_design3.png';

const HowItWorks = () => {
  const [activeImage, setActiveImage] = useState(null);

  const images = [
    {
      id: 1,
      src: ProjectImg1,
      header: 'Upload Your Files',
      description: 'Effortlessly upload your CVs and JDs. Our platform supports various file formats, ensuring a seamless experience.'
    },
    {
      id: 2,
      src: ProjectImg2,
      header: 'Match CVs to Job Descriptions',
      description: 'Select a Job Description and instantly see which CVs are the best fit, ranked by our AI for precision.'
    },
    {
      id: 3,
      src: ProjectImg3,
      header: 'Match Job Descriptions to CVs',
      description: 'Choose a CV to find the most suitable Job Descriptions, saving you time and ensuring you find the perfect role for each candidate.'
    }
  ];

  const handleImageClick = (id) => {
    setActiveImage(id);
  };

  const handleNext = () => {
    if (activeImage < images.length) {
      setActiveImage(activeImage + 1);
    }
  };

  const handlePrevious = () => {
    if (activeImage > 1) {
      setActiveImage(activeImage - 1);
    }
  };

  const handleClose = () => {
    setActiveImage(null);
  };

  return (
    <div id="projects" className={styles.howitworks}>
      {/* <h2>How It Works</h2> */}
      <div className={styles.cards}>
        {images.map((image) => (
          <div key={image.id} className={styles.card}>
            <img src={image.src} alt={image.header} onClick={() => handleImageClick(image.id)} />
            <h3>{image.header}</h3>
            <p>{image.description}</p>
          </div>
        ))}
      </div>
      
      {activeImage && (
        <div className={styles.overlay}>
          <div className={styles.largeImage}>
            <img src={images[activeImage - 1].src} alt={images[activeImage - 1].header} />
            <button className={styles.closeButton} onClick={handleClose}>✖</button>
            {activeImage > 1 && <button className={styles.prevButton} onClick={handlePrevious}>🡰</button>}
            {activeImage < images.length && <button className={styles.nextButton} onClick={handleNext}>🡲</button>}
          </div>
        </div>
      )}
    </div>
  );
};

export default HowItWorks;
