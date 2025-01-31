import { useMsal } from '@azure/msal-react';
import { Alert, Card, Form, Input, Space, Typography } from 'antd';
import React, { useState } from 'react';
import { UserDetails, searchUser, updateUserLimits } from '../../services/userService';
import commonStyles from '../../styles/common.module.css';

const { Title, Text } = Typography;

export const UserManagement: React.FC = () => {
    const { instance } = useMsal();
    const [searchQuery, setSearchQuery] = useState('');
    const [userDetails, setUserDetails] = useState<UserDetails | null>(null);
    const [filesLimit, setFilesLimit] = useState('');
    const [matchingLimit, setMatchingLimit] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleSearch = async () => {
        if (!searchQuery.trim()) return;

        setLoading(true);
        setError('');
        setSuccess('');

        try {
            const account = instance.getActiveAccount();
            if (!account) {
                throw new Error('No active account');
            }

            const data = await searchUser(searchQuery, account, instance);
            setUserDetails(data);
            setFilesLimit(data.filesLimit.toString());
            setMatchingLimit(data.matchingLimit.toString());
        } catch (err) {
            setError('Failed to find user. Please try again.');
            setUserDetails(null);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateLimits = async () => {
        if (!userDetails) return;

        setLoading(true);
        setError('');
        setSuccess('');

        try {
            const account = instance.getActiveAccount();
            if (!account) {
                throw new Error('No active account');
            }

            const updatedUser = await updateUserLimits(
                userDetails.userId,
                parseInt(filesLimit),
                parseInt(matchingLimit),
                account,
                instance
            );
            setUserDetails(updatedUser);
            setSuccess('User limits updated successfully');
        } catch (err) {
            setError('Failed to update limits. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: 24 }}>
            <Title level={4}>User Management</Title>

            <Card style={{ marginBottom: 16 }}>
                <Space.Compact style={{ width: '100%' }}>
                    <Input
                        placeholder="Search by name, email, or ID"
                        value={searchQuery}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
                        style={{ width: '80%' }}
                    />
                    <button
                        className={commonStyles.primaryButton}
                        onClick={handleSearch}
                        disabled={loading}
                        style={{ width: '20%' }}
                    >
                        {loading ? 'Searching...' : 'Search'}
                    </button>
                </Space.Compact>
            </Card>

            {error && (
                <Alert
                    message={error}
                    type="error"
                    showIcon
                    style={{ marginBottom: 16 }}
                />
            )}

            {success && (
                <Alert
                    message={success}
                    type="success"
                    showIcon
                    style={{ marginBottom: 16 }}
                />
            )}

            {userDetails && (
                <Card>
                    <Title level={5}>User Details</Title>
                    <Space direction="vertical" style={{ width: '100%' }}>
                        <Text strong>Name:</Text>
                        <Text>{userDetails.name}</Text>
                        <Text strong>Email:</Text>
                        <Text>{userDetails.email}</Text>
                        <Text strong>User ID:</Text>
                        <Text>{userDetails.userId}</Text>
                        <Text strong>Current Files:</Text>
                        <Text>{userDetails.filesCount}</Text>
                        <Text strong>Matching Used:</Text>
                        <Text>{userDetails.matchingUsedCount}</Text>

                        <Form layout="vertical" style={{ marginTop: 16 }}>
                            <Form.Item label="Files Limit">
                                <Input
                                    type="number"
                                    value={filesLimit}
                                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFilesLimit(e.target.value)}
                                />
                            </Form.Item>

                            <Form.Item label="Matching Limit">
                                <Input
                                    type="number"
                                    value={matchingLimit}
                                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMatchingLimit(e.target.value)}
                                />
                            </Form.Item>

                            <Form.Item>
                                <button
                                    className={commonStyles.primaryButton}
                                    onClick={handleUpdateLimits}
                                    disabled={loading}
                                >
                                    {loading ? 'Updating...' : 'Update Limits'}
                                </button>
                            </Form.Item>
                        </Form>
                    </Space>
                </Card>
            )}
        </div>
    );
}; 