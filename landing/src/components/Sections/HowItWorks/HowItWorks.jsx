import React from "react";
import styles from './HowItWorks.module.css';
import CarouselWrapper from "../../CarouselWrapper/CarouselWrapper";

export default function HowItWorks({handleOpenContactForm}) {
  return (
    <section id="projects" className={styles.wrapper}>
      <div className={styles.content}>
        <div className={styles.headerInfo}>
          <h1 className="font40 extraBold">How it works</h1>
          <p className="font13">
            Simply upload your files and relax, let our advanced AI do the heavy lifting!
          </p>
        </div>
        <CarouselWrapper />
      </div>
    </section>
  );
} 