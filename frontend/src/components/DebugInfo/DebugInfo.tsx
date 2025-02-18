import React, { useEffect, useRef, useState } from 'react';
import { AuthContextType, useAuth } from '../../contexts/AuthContext';
import styles from './DebugInfo.module.css';

interface DebugInfoProps {
    claims: AuthContextType['user'];
}

const isProduction = process.env.NODE_ENV === 'production';

export const DebugInfo: React.FC<DebugInfoProps> = ({ claims }) => {
    const [showDebug, setShowDebug] = useState(false);
    const { user } = useAuth();
    const debugRef = useRef<HTMLDivElement>(null);
    const buttonRef = useRef<HTMLButtonElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (showDebug &&
                debugRef.current &&
                buttonRef.current &&
                !debugRef.current.contains(event.target as Node) &&
                !buttonRef.current.contains(event.target as Node)) {
                setShowDebug(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [showDebug]);

    if (isProduction) {
        return null;
    }

    return (
        <>
            <button
                ref={buttonRef}
                onClick={() => setShowDebug(!showDebug)}
                className={styles.debugButton}
            >
                {showDebug ? 'Hide Debug Info' : 'Show Debug Info'}
            </button>
            {showDebug && (
                <div ref={debugRef} className={styles.debugInfo}>
                    <div>
                        <h4>Basic Info:</h4>
                        <pre>
                            {JSON.stringify({
                                name: user?.name,
                                isAdmin: user?.idTokenClaims?.extension_IsAdmin,
                                isNewUser: user?.isNewUser ?? 'Not available',
                            }, null, 2)}
                        </pre>
                        <h4>ID Token Claims:</h4>
                        <pre>
                            {JSON.stringify(user?.idTokenClaims || 'Not stored in user object', null, 2)}
                        </pre>
                        <h4>Account Info:</h4>
                        <pre>
                            {JSON.stringify(user?.account || 'Not stored in user object', null, 2)}
                        </pre>
                        <h4>Raw User Object:</h4>
                        <pre>
                            {JSON.stringify(user, null, 2)}
                        </pre>
                    </div>
                </div>
            )}
        </>
    );
};