import React from 'react';
import { Spinner as BootstrapSpinner } from 'react-bootstrap';

/**
 * Reusable Spinner component
 * Loading indicators (inline or full-page)
 */
const Spinner = ({
  size = 'md',
  variant = 'primary',
  fullPage = false,
  message = '',
  className = '',
}) => {
  const spinnerSize = size === 'sm' ? 'sm' : undefined;

  const spinner = (
    <>
      <BootstrapSpinner
        animation="border"
        variant={variant}
        size={spinnerSize}
        role="status"
      >
        <span className="visually-hidden">Loading...</span>
      </BootstrapSpinner>
      {message && <div className="mt-2">{message}</div>}
    </>
  );

  if (fullPage) {
    return (
      <div
        className={`d-flex flex-column align-items-center justify-content-center ${className}`}
        style={{ minHeight: '200px' }}
      >
        {spinner}
      </div>
    );
  }

  return <div className={`d-inline-flex align-items-center ${className}`}>{spinner}</div>;
};

export default Spinner;
