import React from 'react';
import { Breadcrumb } from 'react-bootstrap';
import { Link } from 'react-router-dom';

/**
 * Reusable Breadcrumbs component
 * Navigation breadcrumbs for hierarchical pages
 */
const Breadcrumbs = ({
  items = [],
  className = '',
}) => {
  if (!items || items.length === 0) {
    return null;
  }

  return (
    <Breadcrumb className={className}>
      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        return (
          <Breadcrumb.Item
            key={index}
            active={isLast}
            linkAs={!isLast && item.path ? Link : 'span'}
            linkProps={!isLast && item.path ? { to: item.path } : {}}
          >
            {item.label}
          </Breadcrumb.Item>
        );
      })}
    </Breadcrumb>
  );
};

export default Breadcrumbs;
