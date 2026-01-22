import React from 'react';
import { Badge as BootstrapBadge } from 'react-bootstrap';

/**
 * Reusable Badge component
 * Status indicator with various color variants
 */
const Badge = ({
  children,
  variant = 'primary',
  pill = false,
  bg,
  text,
  className = '',
  ...props
}) => {
  return (
    <BootstrapBadge
      bg={bg || variant}
      text={text}
      pill={pill}
      className={className}
      {...props}
    >
      {children}
    </BootstrapBadge>
  );
};

export default Badge;
