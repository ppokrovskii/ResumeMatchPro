import { useMsal } from '@azure/msal-react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

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
        // Handle the redirect promise first
        const result = await instance.handleRedirectPromise();

        // Check for hash parameters even if no result
        const urlParams = new URLSearchParams(window.location.hash.substring(1));
        const error = urlParams.get('error');
        const errorDescription = urlParams.get('error_description');

        if (error) {
          setError({
            errorCode: error,
            errorMessage: decodeURIComponent(errorDescription || 'Unknown error')
          });
          return;
        }

        // Get the account after authentication attempt
        const account = instance.getActiveAccount();
        if (!account) {
          // Try to set the first account as active if available
          const accounts = instance.getAllAccounts();
          if (accounts.length > 0) {
            instance.setActiveAccount(accounts[0]);
          }
        }

        // Always navigate back to home after processing
        navigate('/', { replace: true });
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