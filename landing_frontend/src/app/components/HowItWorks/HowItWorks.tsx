'use client';

import React from 'react';
import Image from 'next/image';
import Button from '../buttons/Button';
import styles from './HowItWorks.module.css';
import Carousel from '../Carousel/Carousel';

const HowItWorks: React.FC = () => {
    const carouselItems = [
        '/images/HowItWorks_1.png',
        '/images/HowItWorks_2.png',
        '/images/HowItWorks_3.png',
    ];

    return (
        <div className={styles.howItWorks}>
            <div className={styles.textContainer}>
                <h1 className={styles.h1}>
                    How it works
                </h1>
                <p className={styles.p}>
                    Simply upload your files and relax, let our advanced AI do the heavy lifting!
                </p>
                <Button className={styles.button} variant="primary">Get Early Access</Button>
            </div>
            <Carousel images={carouselItems} />
        </div>
    );
};

export default HowItWorks;
