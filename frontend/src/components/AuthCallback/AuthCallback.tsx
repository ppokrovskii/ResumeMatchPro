import React, { useEffect } from 'react';
import { useMsal } from '@azure/msal-react';
import { useNavigate } from 'react-router-dom';
import { loginRequest } from '../../authConfig';

const AuthCallback: React.FC = () => {
  const { instance } = useMsal();
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        await instance.handleRedirectPromise();
        const account = instance.getActiveAccount();
        if (!account) {
          // If no active account, try to acquire token silently
          await instance.acquireTokenSilent(loginRequest);
        }
        navigate('/');
      } catch (error) {
        // Log error and redirect to home page
        console.error('Authentication callback error:', error);
        navigate('/');
      }
    };

    handleCallback();
  }, [instance, navigate]);

  return (
    <div className="auth-callback">
      <p>Processing authentication...</p>
    </div>
  );
};

export default AuthCallback; 