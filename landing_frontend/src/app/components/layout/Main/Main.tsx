import Button from "../../buttons/Button";
import Section from "../Section/Section";

const Main = () => {
    return (
        <main className="container pt-32">
            <Section>
                <h1 className="text-5xl sm:text-7xl lg:text-8xl font-semibold mb-4">
                    Speed Up Recruitment with AI-Driven CV Screening
                </h1>
                <p className="mb-4">
                    Leverage our advanced AI to quickly filter and match CVs with job descriptions, streamlining your hiring process. Focus more on engaging candidates and less on sifting through CVs.
                </p>
                <Button className="grow" variant="primary">Get Early Access</Button>
            </Section>
            <Section>
                <h1 className="text-5xl sm:text-7xl lg:text-8xl font-semibold mb-4">
                    Increase Your Chances of Landing an Interview
                </h1>
                <p className="mb-4">
                    Use our advanced AI to tailor your resume to job descriptions, boosting your interview prospects. Focus more on preparing for interviews and less on manual resume adjustments.
                </p>
                <Button className="grow" variant="primary">Get Early Access</Button>
            </Section>
            <Section>
                <h1 className="text-5xl sm:text-7xl lg:text-8xl font-semibold mb-4">
                    How it works
                </h1>
                <p className="mb-4">
                    Simply upload your files and relax, let our advanced AI do the heavy lifting!
                </p>
                <Button className="grow" variant="primary">Get Early Access</Button>
            </Section>
            <Section>
                <h1 className="text-5xl sm:text-7xl lg:text-8xl font-semibold mb-4">
                    Signup for an early access!
                </h1>
                <p className="mb-4">
                    Get notified when beta testing starts. Receive updates on our latest features and services.
                </p>
                <Button className="grow" variant="primary">Get Early Access</Button>
            </Section>
            <Section>
                <div className="flex justify-center">
                    <div className="flex flex-col gap-2">
                        <Button className="grow">Regular Button</Button>
                        <Button className="grow" variant="primary">Primary Button</Button>
                        <Button className="grow" variant="secondary">Secondary Button</Button>
                        <Button className="grow" variant="accent">Accent Button</Button>
                    </div>
                </div>
            </Section>
        </main>
    );
};

export default Main;
