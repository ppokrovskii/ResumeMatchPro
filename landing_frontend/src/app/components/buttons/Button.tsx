// src/components/Buttons/Button.tsx
import styles from './Button.module.css';

type ButtonProps = {
    variant?: 'primary' | 'secondary'; // Make the variant prop optional
    children: React.ReactNode;
};

const Button = ({ variant = 'primary', children }: ButtonProps) => { // Set 'primary' as the default value for variant
    return <button className={styles[variant]}>{children}</button>;
};

export default Button;
