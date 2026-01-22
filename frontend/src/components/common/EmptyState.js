import React from 'react';
import Button from './Button';

/**
 * EmptyState component
 * Display when lists are empty with icon, text, and optional CTA
 */
const EmptyState = ({
  icon,
  title,
  message,
  actionLabel,
  onAction,
  className = '',
}) => {
  return (
    <div className={`text-center py-5 ${className}`}>
      {icon && (
        <div className="mb-3">
          <i className={`${icon} fs-1 text-muted`} />
        </div>
      )}
      {title && <h5 className="text-muted mb-2">{title}</h5>}
      {message && <p className="text-muted mb-3">{message}</p>}
      {actionLabel && onAction && (
        <Button variant="primary" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

export default EmptyState;
