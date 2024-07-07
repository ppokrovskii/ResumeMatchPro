import Image from 'next/image';
import Button from '../buttons/Button';
import styles from './JobSeeker.module.css';
import React from 'react';

{/* <div className="container">
                        <h1 className="text-5xl sm:text-7xl lg:text-8xl font-semibold mb-4">
                            Increase Your Chances of Landing an Interview
                        </h1>
                        <p className="mb-4">
                            Use our advanced AI to tailor your resume to job descriptions, boosting your interview prospects. Focus more on preparing for interviews and less on manual resume adjustments.
                        </p>
                        <Button className="grow" variant="primary">Get Early Access</Button>
                    </div> */}

const JobSeeker = () => {
    return (
        <div className={styles.jobSeeker}>
            <div className={styles.textContainer}>
                <h1 className={styles.h1}>
                    Increase Your Chances of Landing an Interview
                </h1>
                <p className={styles.p}>
                    Use our advanced AI to tailor your resume to job descriptions, boosting your interview prospects. Focus more on preparing for interviews and less on manual resume adjustments.
                </p>
                <Button variant="primary">Get Early Access</Button>
            </div>
            {/* <div className={styles.imageContainer}>
                <Image
                    src="/images/JobSeeker.png"
                    alt="JobSeeker"
                    layout="fill"
                    className={styles.img}
                />
            </div> */}
        </div>
    );
};

export default JobSeeker;
