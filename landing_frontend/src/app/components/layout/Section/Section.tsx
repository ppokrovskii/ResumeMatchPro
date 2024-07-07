import React, { ReactNode } from 'react';
// import './Section.css';

interface SectionProps {
    children: ReactNode;
}

const Section: React.FC<SectionProps> = ({ children }) => {
    return (
        <section className="mx-auto p-8">
            <div className="section-content">{children}</div>
        </section>
    );
};

export default Section;