import React from 'react';
import { Button as BootstrapButton } from 'react-bootstrap';

/**
 * Reusable Button component
 * Wrapper around react-bootstrap Button with consistent styling
 */
const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  type = 'button',
  disabled = false,
  loading = false,
  onClick,
  className = '',
  fullWidth = false,
  ...props
}) => {
  return (
    <BootstrapButton
      variant={variant}
      size={size}
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={`${fullWidth ? 'w-100' : ''} ${className}`}
      aria-busy={loading}
      {...props}
    >
      {loading ? (
        <>
          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
          <span className="sr-only">Loading...</span>
          {children}
        </>
      ) : (
        children
      )}
    </BootstrapButton>
  );
};

export default Button;
