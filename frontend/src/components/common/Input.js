import React from 'react';
import { Form } from 'react-bootstrap';

/**
 * Reusable Input component
 * Text/email/password input with validation states
 */
const Input = ({
  type = 'text',
  value,
  onChange,
  onBlur,
  placeholder = '',
  disabled = false,
  required = false,
  error = '',
  name,
  id,
  autoComplete,
  className = '',
  ...props
}) => {
  // Handle error as either string or object with error property
  const errorMessage = typeof error === 'object' ? error?.error : error;
  const hasError = Boolean(errorMessage);

  return (
    <>
      <Form.Control
        type={type}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        isInvalid={hasError}
        name={name}
        id={id}
        autoComplete={autoComplete}
        className={className}
        {...props}
      />
      {hasError && (
        <Form.Control.Feedback type="invalid">
          {errorMessage}
        </Form.Control.Feedback>
      )}
    </>
  );
};

export default Input;
