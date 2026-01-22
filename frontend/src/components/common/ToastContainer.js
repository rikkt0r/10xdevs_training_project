import React from 'react';
import { ToastContainer as BootstrapToastContainer } from 'react-bootstrap';

/**
 * Container for displaying multiple toast notifications
 */
const ToastContainer = ({
  children,
  position = 'top-end',
  className = '',
}) => {
  return (
    <BootstrapToastContainer
      position={position}
      className={`p-3 ${className}`}
      style={{ zIndex: 9999 }}
    >
      {children}
    </BootstrapToastContainer>
  );
};

export default ToastContainer;
