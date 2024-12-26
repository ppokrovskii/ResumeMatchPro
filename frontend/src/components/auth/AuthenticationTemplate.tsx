import React from 'react';
import { MsalAuthenticationTemplate } from '@azure/msal-react';
import { InteractionType } from '@azure/msal-browser';
import { loginRequest } from '../../authConfig';

interface Props {
  children: React.ReactNode;
}

export const AuthenticationTemplate: React.FC<Props> = ({ children }) => {
  const ErrorComponent = ({ error }: { error: any }) => {
    if (error?.errorMessage?.includes('AADB2C90091')) {
      return null;
    }
    return (
      <div className="auth-error">
        Authentication failed. Please try again.
      </div>
    );
  };

  const LoadingComponent = () => (
    <div className="auth-callback">
      <p>Processing authentication...</p>
    </div>
  );

  return (
    <MsalAuthenticationTemplate 
      interactionType={InteractionType.Redirect}
      authenticationRequest={loginRequest}
      errorComponent={ErrorComponent}
      loadingComponent={LoadingComponent}
    >
      {children}
    </MsalAuthenticationTemplate>
  );
}; 