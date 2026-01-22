import React from 'react';
import { formatRelativeDate } from '../../utils/dateUtils';
import { useTranslation } from 'react-i18next';
import Badge from './Badge';

/**
 * Timeline component
 * Display chronological events (e.g., ticket status history)
 */
const Timeline = ({
  items = [],
  className = '',
}) => {
  const { i18n } = useTranslation();

  if (!items || items.length === 0) {
    return null;
  }

  return (
    <div className={`timeline ${className}`}>
      {items.map((item, index) => (
        <div key={index} className="timeline-item d-flex mb-3">
          <div className="timeline-marker me-3">
            <div
              className={`timeline-dot bg-${item.variant || 'primary'}`}
              style={{
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                marginTop: '5px'
              }}
            />
            {index < items.length - 1 && (
              <div
                className="timeline-line bg-secondary"
                style={{
                  width: '2px',
                  height: 'calc(100% + 12px)',
                  marginLeft: '5px',
                  opacity: 0.3
                }}
              />
            )}
          </div>

          <div className="timeline-content flex-grow-1">
            <div className="d-flex justify-content-between align-items-start mb-1">
              <div>
                <strong>{item.title}</strong>
                {item.badge && (
                  <Badge variant={item.badgeVariant || 'secondary'} className="ms-2">
                    {item.badge}
                  </Badge>
                )}
              </div>
              <small className="text-muted">
                {formatRelativeDate(item.date, i18n.language)}
              </small>
            </div>

            {item.description && (
              <p className="text-muted mb-1">{item.description}</p>
            )}

            {item.user && (
              <small className="text-muted">
                <i className="bi bi-person me-1" />
                {item.user}
              </small>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default Timeline;
