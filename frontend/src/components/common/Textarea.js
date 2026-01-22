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
  const hasError = Boolean(error);
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
          {error}
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
