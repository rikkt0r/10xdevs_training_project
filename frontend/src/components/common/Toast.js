import React from 'react';
import { Toast as BootstrapToast } from 'react-bootstrap';

/**
 * Individual Toast notification component
 */
const Toast = ({
  show = true,
  onClose,
  title,
  message,
  variant = 'info',
  autoHide = true,
  delay = 5000,
  className = '',
}) => {
  const bgClass = variant ? `bg-${variant} text-white` : '';

  return (
    <BootstrapToast
      show={show}
      onClose={onClose}
      autohide={autoHide}
      delay={delay}
      className={`${bgClass} ${className}`}
    >
      {title && (
        <BootstrapToast.Header>
          <strong className="me-auto">{title}</strong>
        </BootstrapToast.Header>
      )}
      <BootstrapToast.Body className={variant === 'light' ? 'text-dark' : ''}>
        {message}
      </BootstrapToast.Body>
    </BootstrapToast>
  );
};

export default Toast;
