import Button from "../../buttons/Button";
import HR from "../../HR/HR";
import styles from "./Main.module.css";

const Main = () => {
    return (
        <main className={styles.main}>
            <div className={styles.section}>
                <div className={styles.sectionContent}>
                    <HR />
                </div>
            </div>
            <div className={`${styles.section}` + " bg-bg-secondary"}>
                <div className={styles.sectionContent}>
                    <div className="container">
                        <h1 className="text-5xl sm:text-7xl lg:text-8xl font-semibold mb-4">
                            Increase Your Chances of Landing an Interview
                        </h1>
                        <p className="mb-4">
                            Use our advanced AI to tailor your resume to job descriptions, boosting your interview prospects. Focus more on preparing for interviews and less on manual resume adjustments.
                        </p>
                        <Button className="grow" variant="primary">Get Early Access</Button>
                    </div>
                </div>
            </div>
            <div className={`${styles.section}`}>
                <h1 className="text-5xl sm:text-7xl lg:text-8xl font-semibold mb-4">
                    How it works
                </h1>
                <p className="mb-4">
                    Simply upload your files and relax, let our advanced AI do the heavy lifting!
                </p>
                <Button className="grow" variant="primary">Get Early Access</Button>
            </div>
            <div className={`${styles.section}`}>
                <h1 className="text-5xl sm:text-7xl lg:text-8xl font-semibold mb-4">
                    Signup for an early access!
                </h1>
                <p className="mb-4">
                    Get notified when beta testing starts. Receive updates on our latest features and services.
                </p>
                <Button className="grow" variant="primary">Get Early Access</Button>
            </div>
            <div className={`${styles.section}`}>
                <div className="flex justify-center">
                    <div className="flex flex-col gap-2">
                        <Button className="grow">Regular Button</Button>
                        <Button className="grow" variant="primary">Primary Button</Button>
                        <Button className="grow" variant="secondary">Secondary Button</Button>
                        <Button className="grow" variant="accent">Accent Button</Button>
                    </div>
                </div>
            </div>
        </main>
    );
};

export default Main;
