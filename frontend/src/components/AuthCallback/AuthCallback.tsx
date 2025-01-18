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
        // Check if there's an error in the URL hash
        const urlParams = new URLSearchParams(window.location.hash.substring(1));
        const error = urlParams.get('error');
        const errorDescription = urlParams.get('error_description');

        if (error) {
          // If there's an error, set it and don't redirect
          setError({
            errorCode: error,
            errorMessage: decodeURIComponent(errorDescription || 'Unknown error')
          });
          return;
        }

        // No error, proceed with normal flow
        await instance.handleRedirectPromise();
        const account = instance.getActiveAccount();
        if (!account) {
          await instance.acquireTokenSilent(loginRequest);
        }
        navigate('/');
      } catch (error) {
        console.error('Authentication callback error:', error);
        setError({
          errorCode: 'unknown_error',
          errorMessage: 'An unexpected error occurred during authentication.'
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