/**
 * Validate email format
 * @param {string} email - Email address to validate
 * @returns {boolean}
 */
export const validateEmail = (email) => {
  if (!email) return false;

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @param {number} minLength - Minimum password length (default: 8)
 * @returns {object} Validation result with isValid and errors
 */
export const validatePassword = (password, minLength = 8) => {
  const errors = [];

  if (!password) {
    return { isValid: false, errors: ['Password is required'] };
  }

  if (password.length < minLength) {
    errors.push(`Password must be at least ${minLength} characters`);
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Validate required field
 * @param {any} value - Value to validate
 * @param {string} fieldName - Field name for error message
 * @returns {object} Validation result
 */
export const validateRequired = (value, fieldName = 'This field') => {
  const isEmpty = value === null || value === undefined || value === '' ||
                  (Array.isArray(value) && value.length === 0);

  return {
    isValid: !isEmpty,
    error: isEmpty ? `${fieldName} is required` : null
  };
};

/**
 * Validate maximum length
 * @param {string} value - Value to validate
 * @param {number} maxLength - Maximum allowed length
 * @param {string} fieldName - Field name for error message
 * @returns {object} Validation result
 */
export const validateMaxLength = (value, maxLength, fieldName = 'This field') => {
  if (!value) {
    return { isValid: true, error: null };
  }

  const isTooLong = value.length > maxLength;

  return {
    isValid: !isTooLong,
    error: isTooLong ? `${fieldName} must not exceed ${maxLength} characters` : null
  };
};

/**
 * Validate alphanumeric with hyphens (lowercase only)
 * @param {string} value - Value to validate
 * @param {string} fieldName - Field name for error message
 * @returns {object} Validation result
 */
export const validateAlphanumericHyphen = (value, fieldName = 'This field') => {
  if (!value) {
    return { isValid: true, error: null };
  }

  const alphanumericHyphenRegex = /^[a-z0-9-]+$/;
  const isValid = alphanumericHyphenRegex.test(value);

  return {
    isValid,
    error: isValid ? null : `${fieldName} can only contain lowercase letters, numbers, and hyphens`
  };
};

/**
 * Validate password confirmation
 * @param {string} password - Original password
 * @param {string} confirmPassword - Password confirmation
 * @returns {object} Validation result
 */
export const validatePasswordConfirmation = (password, confirmPassword) => {
  if (!confirmPassword) {
    return { isValid: false, error: 'Please confirm your password' };
  }

  if (password !== confirmPassword) {
    return { isValid: false, error: 'Passwords do not match' };
  }

  return { isValid: true, error: null };
};

/**
 * Validate URL format
 * @param {string} url - URL to validate
 * @returns {boolean}
 */
export const validateUrl = (url) => {
  if (!url) return false;

  try {
    new URL(url);
    return true;
  } catch (error) {
    return false;
  }
};

/**
 * Validate port number
 * @param {number|string} port - Port number to validate
 * @returns {object} Validation result
 */
export const validatePort = (port) => {
  const portNum = parseInt(port, 10);

  if (isNaN(portNum)) {
    return { isValid: false, error: 'Port must be a number' };
  }

  if (portNum < 1 || portNum > 65535) {
    return { isValid: false, error: 'Port must be between 1 and 65535' };
  }

  return { isValid: true, error: null };
};

/**
 * Validate number range
 * @param {number} value - Value to validate
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {object} Validation result
 */
export const validateRange = (value, min, max) => {
  const num = parseFloat(value);

  if (isNaN(num)) {
    return { isValid: false, error: 'Must be a number' };
  }

  if (num < min || num > max) {
    return { isValid: false, error: `Must be between ${min} and ${max}` };
  }

  return { isValid: true, error: null };
};

/**
 * Sanitize text input (remove dangerous characters)
 * @param {string} text - Text to sanitize
 * @returns {string} Sanitized text
 */
export const sanitizeText = (text) => {
  if (!text) return '';

  return text
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
};
