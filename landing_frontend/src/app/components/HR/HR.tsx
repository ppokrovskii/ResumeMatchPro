import Image from 'next/image';
import Button from '../buttons/Button';
import styles from './HR.module.css';
import React from 'react';

const HR = () => {
    return (
        <div className={styles.hr}>
            <div className={styles.textContainer}>
                <h1 className={styles.h1}>
                    Speed Up Recruitment with AI-Driven CV Screening
                </h1>
                <p className={styles.p}>
                    Leverage our advanced AI to quickly filter and match CVs with job descriptions, streamlining your hiring process. Focus more on engaging candidates and less on sifting through CVs.
                </p>
                <Button variant="primary">Get Early Access</Button>
            </div>
            <div className={styles.imageContainer}>
                <Image 
                    src="/images/hr.png" 
                    alt="HR" 
                    layout="fill" 
                    className={styles.img} 
                />
            </div>
        </div>
    );
};

export default HR;
