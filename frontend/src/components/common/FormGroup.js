import React from 'react';
import { Form } from 'react-bootstrap';

/**
 * Reusable FormGroup component
 * Wrapper that combines label, input/select/textarea, and error display
 */
const FormGroup = ({
  label,
  required = false,
  error = '',
  helpText = '',
  className = '',
  children,
  htmlFor,
}) => {
  const hasError = Boolean(error);

  return (
    <Form.Group className={`mb-3 ${className}`}>
      {label && (
        <Form.Label htmlFor={htmlFor}>
          {label}
          {required && <span className="text-danger ms-1">*</span>}
        </Form.Label>
      )}
      {children}
      {helpText && !hasError && (
        <Form.Text className="text-muted d-block">
          {helpText}
        </Form.Text>
      )}
      {hasError && (
        <div className="invalid-feedback d-block">
          {error}
        </div>
      )}
    </Form.Group>
  );
};

export default FormGroup;
