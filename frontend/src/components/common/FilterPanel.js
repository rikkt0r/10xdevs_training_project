import React, { useState } from 'react';
import { Collapse, Card } from 'react-bootstrap';
import Badge from './Badge';
import Button from './Button';

/**
 * FilterPanel component
 * Collapsible filters panel with active count badge
 */
const FilterPanel = ({
  title = 'Filters',
  children,
  activeFiltersCount = 0,
  onClear,
  defaultOpen = false,
  className = '',
}) => {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <Card className={`mb-3 ${className}`}>
      <Card.Header>
        <div className="d-flex justify-content-between align-items-center">
          <div
            className="d-flex align-items-center"
            style={{ cursor: 'pointer' }}
            onClick={() => setOpen(!open)}
          >
            <i className={`bi bi-funnel me-2`} />
            <strong>{title}</strong>
            {activeFiltersCount > 0 && (
              <Badge variant="primary" pill className="ms-2">
                {activeFiltersCount}
              </Badge>
            )}
            <i className={`bi bi-chevron-${open ? 'up' : 'down'} ms-2`} />
          </div>

          {activeFiltersCount > 0 && onClear && (
            <Button
              variant="link"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onClear();
              }}
              className="text-decoration-none p-0"
            >
              Clear all
            </Button>
          )}
        </div>
      </Card.Header>

      <Collapse in={open}>
        <Card.Body>{children}</Card.Body>
      </Collapse>
    </Card>
  );
};

export default FilterPanel;
