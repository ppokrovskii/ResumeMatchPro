import Button from "../../buttons/Button";
import HowItWorks from "../../HowItWorks/HowItWorks";
import HR from "../../HR/HR";
import JobSeeker from "../../JobSeeker/JobSeeker";
import styles from "./Main.module.css";

const Main = () => {
    return (
        <main className={styles.main}>
            <div className={styles.section}>
                <div className={styles.sectionContent}>
                    <HR />
                </div>
            </div>
            <div className={`${styles.section} ${styles.bgJobSeeker}`}>
                <div className={styles.sectionContent}>
                    <JobSeeker />
                </div>
            </div>
            <div className={styles.section}>
                <HowItWorks /> 
            </div>
            <div className={styles.section}>
                <h1 className={styles.heading}>
                    Signup for an early access!
                </h1>
                <p className={styles.paragraph}>
                    Get notified when beta testing starts. Receive updates on our latest features and services.
                </p>
                <Button className={styles.button} variant="primary">Get Early Access</Button>
            </div>
            <div className={styles.section}>
                <div className="flex justify-center">
                    <div className="flex flex-col gap-2">
                        <Button className={styles.button}>Regular Button</Button>
                        <Button className={styles.button} variant="primary">Primary Button</Button>
                        <Button className={styles.button} variant="secondary">Secondary Button</Button>
                        <Button className={styles.button} variant="accent">Accent Button</Button>
                    </div>
                </div>
            </div>
        </main>
    );
};

export default Main;