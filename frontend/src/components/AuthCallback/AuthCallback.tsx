import React, { useEffect } from 'react';
import { useMsal } from '@azure/msal-react';
import { useNavigate } from 'react-router-dom';

const AuthCallback: React.FC = () => {
  const { instance } = useMsal();
  const navigate = useNavigate();

  useEffect(() => {
    instance
      .handleRedirectPromise()
      .then((response) => {
        if (response) {
          console.log('Authentication successful:', response);
          navigate('/');
        }
      })
      .catch((error) => {
        console.error('Authentication error:', error);
        
        // Handle user cancellation gracefully
        if (error.errorMessage?.includes('AADB2C90091')) {
          console.log('User cancelled sign-up/sign-in');
          // Just redirect to home page without error
          navigate('/');
          return;
        }

        // Handle other errors
        navigate('/', { 
          state: { 
            authError: 'Authentication failed. Please try again.' 
          }
        });
      });
  }, [instance, navigate]);

  return (
    <div className="auth-callback">
      <p>Processing authentication...</p>
    </div>
  );
};

export default AuthCallback; 