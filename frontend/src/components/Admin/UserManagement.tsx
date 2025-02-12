import { useMsal } from '@azure/msal-react';
import { Alert, Card, Form, Input, List, Space, Typography } from 'antd';
import React, { useState } from 'react';
import { UserDetails, searchUser, updateUserLimits } from '../../services/userService';
import commonStyles from '../../styles/common.module.css';

const { Title, Text } = Typography;

export const UserManagement: React.FC = () => {
    const { instance } = useMsal();
    const [searchQuery, setSearchQuery] = useState('');
    const [users, setUsers] = useState<UserDetails[]>([]);
    const [selectedUser, setSelectedUser] = useState<UserDetails | null>(null);
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
        setSelectedUser(null);

        try {
            const account = instance.getActiveAccount();
            if (!account) {
                throw new Error('No active account');
            }

            const foundUsers = await searchUser(searchQuery, account, instance);
            setUsers(foundUsers);
            if (foundUsers.length === 0) {
                setError('No users found');
            }
        } catch (err) {
            setError('Failed to find user. Please try again.');
            setUsers([]);
        } finally {
            setLoading(false);
        }
    };

    const handleSelectUser = (user: UserDetails) => {
        setSelectedUser(user);
        setFilesLimit(user.filesLimit.toString());
        setMatchingLimit(user.matchingLimit.toString());
    };

    const handleUpdateLimits = async () => {
        if (!selectedUser) return;

        setLoading(true);
        setError('');
        setSuccess('');

        try {
            const account = instance.getActiveAccount();
            if (!account) {
                throw new Error('No active account');
            }

            const updatedUser = await updateUserLimits(
                selectedUser.userId,
                parseInt(filesLimit),
                parseInt(matchingLimit),
                account,
                instance
            );
            setSelectedUser(updatedUser);
            setUsers(users.map(u => u.userId === updatedUser.userId ? updatedUser : u));
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

            {users.length > 0 && (
                <Card style={{ marginBottom: 16 }}>
                    <Title level={5}>Search Results</Title>
                    <List
                        dataSource={users}
                        renderItem={user => (
                            <List.Item
                                onClick={() => handleSelectUser(user)}
                                style={{ cursor: 'pointer', background: selectedUser?.userId === user.userId ? '#f0f0f0' : 'transparent' }}
                            >
                                <List.Item.Meta
                                    title={user.name}
                                    description={
                                        <Space direction="vertical">
                                            <Text>Email: {user.email}</Text>
                                            <Text>User ID: {user.userId}</Text>
                                        </Space>
                                    }
                                />
                            </List.Item>
                        )}
                    />
                </Card>
            )}

            {selectedUser && (
                <Card>
                    <Title level={5}>Edit User Limits</Title>
                    <Space direction="vertical" style={{ width: '100%' }}>
                        <Text strong>Name:</Text>
                        <Text>{selectedUser.name}</Text>
                        <Text strong>Email:</Text>
                        <Text>{selectedUser.email}</Text>
                        <Text strong>User ID:</Text>
                        <Text>{selectedUser.userId}</Text>
                        <Text strong>Current Files:</Text>
                        <Text>{selectedUser.filesCount}</Text>
                        <Text strong>Matching Used:</Text>
                        <Text>{selectedUser.matchingUsedCount}</Text>

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