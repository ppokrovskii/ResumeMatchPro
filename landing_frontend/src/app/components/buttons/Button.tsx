// src/components/Buttons/Button.tsx
import styles from './Button.module.css';

type ButtonProps = {
    variant?: 'regular' | 'primary' | 'secondary' | 'accent';
    children: React.ReactNode;
    className?: string; // Add className prop to accept additional classes
};

const Button = ({ variant = 'regular', children, className }: ButtonProps) => {
    const buttonClasses = `${styles[variant]} py-2 px-4 rounded-xl ${className}`; // Concatenate the additional classes with the existing classes

    return <button className={buttonClasses}>{children}</button>;
};

export default Button;
