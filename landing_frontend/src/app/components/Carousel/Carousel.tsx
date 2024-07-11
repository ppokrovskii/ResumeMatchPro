'use client';

import React from 'react';
import { Carousel as MTCarousel } from '@material-tailwind/react';
import Image from 'next/image';
import styles from './Carousel.module.css';

interface CarouselProps {
    images: string[];
}

const Carousel: React.FC<CarouselProps> = ({ images }) => {
    return (
        <MTCarousel
            className={styles.carousel}
            placeholder=""
            onPointerEnterCapture={() => { }}
            onPointerLeaveCapture={() => { }}
        >
            {images.map((image, index) => (
                <img
                    key={index}
                    src={image}
                    alt={`Slide ${index + 1}`}
                    className="h-full w-full object-cover"
                />
            ))}
        </MTCarousel>
    );
};

export default Carousel;
