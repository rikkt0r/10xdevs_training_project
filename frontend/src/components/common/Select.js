import React from 'react';
import { Form } from 'react-bootstrap';

/**
 * Reusable Select component
 * Dropdown select with validation
 */
const Select = ({
  value,
  onChange,
  onBlur,
  options = [],
  placeholder = 'Select...',
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
    <>
      <Form.Select
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        disabled={disabled}
        required={required}
        isInvalid={hasError}
        name={name}
        id={id}
        className={className}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option key={option.value} value={option.value} disabled={option.disabled}>
            {option.label}
          </option>
        ))}
      </Form.Select>
      {hasError && (
        <Form.Control.Feedback type="invalid">
          {error}
        </Form.Control.Feedback>
      )}
    </>
  );
};

export default Select;
