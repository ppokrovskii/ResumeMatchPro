import { useMsal } from '@azure/msal-react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginRequest } from '../../authConfig';

interface AuthError {
  errorCode: string;
  errorMessage: string;
}

const AuthCallback: React.FC = () => {
  const { instance } = useMsal();
  const navigate = useNavigate();
  const [error, setError] = useState<AuthError | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        await instance.handleRedirectPromise();
        const account = instance.getActiveAccount();
        if (!account) {
          console.error('No active account found after redirect');
          const accounts = instance.getAllAccounts();
          if (accounts.length > 0) {
            instance.setActiveAccount(accounts[0]);
          } else {
            await instance.loginRedirect(loginRequest);
            return;
          }
        }
        navigate('/');
      } catch (error) {
        console.error('Authentication callback error:', error);
        setError({
          errorCode: 'unknown_error',
          errorMessage: error instanceof Error ? error.message : 'An unexpected error occurred during authentication.'
        });
      }
    };

    handleCallback();
  }, [instance, navigate]);

  if (error) {
    return (
      <div className="auth-error-container">
        <h2>Authentication Error</h2>
        <div className="error-details">
          <p><strong>Error Code:</strong> {error.errorCode}</p>
          <p><strong>Message:</strong> {error.errorMessage}</p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="return-home-button"
        >
          Return to Home
        </button>
      </div>
    );
  }

  return (
    <div className="auth-callback">
      <p>Processing authentication...</p>
    </div>
  );
};

export default AuthCallback; 