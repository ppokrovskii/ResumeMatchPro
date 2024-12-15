import React from "react";
import styles from './Projects.module.css';
import HowItWorksV2 from "../HowItWorksV2/HowItWorksV2";

export default function Projects({handleOpenContactForm}) {
  return (
    <section id="projects" className={styles.wrapper}>
      <div className={styles.content}>
        <div className={styles.headerInfo}>
          <h1 className="font40 extraBold">How it works</h1>
          <p className="font13">
            Simply upload your files and relax, let our advanced AI do the heavy lifting!
          </p>
        </div>
        <HowItWorksV2/>
      </div>
    </section>
  );
} 