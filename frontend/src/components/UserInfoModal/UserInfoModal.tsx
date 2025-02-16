import { useMsal } from '@azure/msal-react';
import { Modal } from 'antd';
import React, { useEffect, useState } from 'react';
import { UserDetails, getCurrentUser } from '../../services/userService';
import styles from './UserInfoModal.module.css';

interface UserInfoModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export const UserInfoModal: React.FC<UserInfoModalProps> = ({ isOpen, onClose }) => {
    const { instance, accounts } = useMsal();
    const [userDetails, setUserDetails] = useState<UserDetails | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchUserDetails = async () => {
            if (!isOpen || !accounts[0]) return;

            try {
                setLoading(true);
                setError(null);
                const details = await getCurrentUser(accounts[0], instance);
                setUserDetails(details);
            } catch (err) {
                setError('Failed to load user details');
                console.error('Error loading user details:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchUserDetails();
    }, [isOpen, accounts, instance]);

    return (
        <Modal
            title="User Information"
            open={isOpen}
            onCancel={onClose}
            footer={null}
            className={styles.modal}
        >
            {loading ? (
                <div>Loading...</div>
            ) : error ? (
                <div className={styles.error}>{error}</div>
            ) : userDetails ? (
                <div className={styles.userInfo}>
                    <h2>{userDetails.name}</h2>
                    <p><strong>Email:</strong> {userDetails.email}</p>
                    <p><strong>User ID:</strong> {userDetails.userId}</p>
                    <p><strong>Files:</strong> {userDetails.filesCount}/{userDetails.filesLimit}</p>
                    <p><strong>Matches:</strong> {userDetails.matchingUsedCount}/{userDetails.matchingLimit}</p>
                </div>
            ) : null}
        </Modal>
    );
}; 