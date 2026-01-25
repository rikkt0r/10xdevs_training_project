import React from 'react';
import { Form } from 'react-bootstrap';

/**
 * Reusable Textarea component
 * Multi-line text input with optional character counter
 */
const Textarea = ({
  value,
  onChange,
  onBlur,
  placeholder = '',
  disabled = false,
  required = false,
  error = '',
  rows = 3,
  maxLength,
  showCharCount = false,
  name,
  id,
  className = '',
  ...props
}) => {
  // Handle error as either string or object with error property
  const errorMessage = typeof error === 'object' ? error?.error : error;
  const hasError = Boolean(errorMessage);
  const charCount = value ? value.length : 0;

  return (
    <>
      <Form.Control
        as="textarea"
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        isInvalid={hasError}
        rows={rows}
        maxLength={maxLength}
        name={name}
        id={id}
        className={className}
        {...props}
      />
      {hasError && (
        <Form.Control.Feedback type="invalid">
          {errorMessage}
        </Form.Control.Feedback>
      )}
      {showCharCount && (
        <Form.Text className="text-muted d-block text-end">
          {charCount}{maxLength ? ` / ${maxLength}` : ''} characters
        </Form.Text>
      )}
    </>
  );
};

export default Textarea;
