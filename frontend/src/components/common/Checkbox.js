import React from 'react';
import { Form } from 'react-bootstrap';

/**
 * Reusable Checkbox component
 * Checkbox with label and validation
 */
const Checkbox = ({
  checked,
  onChange,
  label,
  disabled = false,
  required = false,
  error = '',
  name,
  id,
  className = '',
  ...props
}) => {
  const hasError = Boolean(error);

  return (
    <div className={className}>
      <Form.Check
        type="checkbox"
        checked={checked}
        onChange={onChange}
        label={label}
        disabled={disabled}
        required={required}
        isInvalid={hasError}
        name={name}
        id={id}
        {...props}
      />
      {hasError && (
        <Form.Control.Feedback type="invalid" className="d-block">
          {error}
        </Form.Control.Feedback>
      )}
    </div>
  );
};

export default Checkbox;
