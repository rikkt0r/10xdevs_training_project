import React from 'react';
import { Card as BootstrapCard } from 'react-bootstrap';

/**
 * Reusable Card component
 * Wrapper around react-bootstrap Card with slots for header, body, and footer
 */
const Card = ({
  children,
  header,
  footer,
  title,
  subtitle,
  className = '',
  bodyClassName = '',
  ...props
}) => {
  return (
    <BootstrapCard className={className} {...props}>
      {(header || title) && (
        <BootstrapCard.Header>
          {header || (
            <>
              {title && <BootstrapCard.Title>{title}</BootstrapCard.Title>}
              {subtitle && <BootstrapCard.Subtitle className="text-muted">{subtitle}</BootstrapCard.Subtitle>}
            </>
          )}
        </BootstrapCard.Header>
      )}

      <BootstrapCard.Body className={bodyClassName}>
        {children}
      </BootstrapCard.Body>

      {footer && (
        <BootstrapCard.Footer>
          {footer}
        </BootstrapCard.Footer>
      )}
    </BootstrapCard>
  );
};

export default Card;
