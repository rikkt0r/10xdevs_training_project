import React from 'react';
import { Alert as BootstrapAlert } from 'react-bootstrap';

/**
 * Reusable Alert component
 * Feedback messages for success/error/warning/info
 */
const Alert = ({
  children,
  variant = 'info',
  dismissible = false,
  onClose,
  show = true,
  className = '',
  ...props
}) => {
  if (!show) return null;

  return (
    <BootstrapAlert
      variant={variant}
      dismissible={dismissible}
      onClose={onClose}
      className={className}
      {...props}
    >
      {children}
    </BootstrapAlert>
  );
};

export default Alert;
