import React from 'react';
import { useTranslation } from 'react-i18next';
import Card from '../common/Card';
import Badge from '../common/Badge';
import Button from '../common/Button';
import { formatRelativeDate } from '../../utils/dateUtils';

/**
 * QueueItemCard component
 * Card view for standby queue item summary
 */
const QueueItemCard = ({ item, onView, onAssign, onRetry, onDiscard }) => {
  const { t, i18n } = useTranslation();

  return (
    <Card className="mb-3">
      <div className="d-flex justify-content-between align-items-start">
        <div className="flex-grow-1">
          {/* Header */}
          <div className="d-flex align-items-center gap-2 mb-2">
            <Badge variant="warning">
              {item.reason || t('standbyQueue.noKeywordMatch') || 'No keyword match'}
            </Badge>
            {item.external_sync_failed && (
              <Badge variant="danger">
                <i className="bi bi-exclamation-triangle me-1" />
                {t('standbyQueue.externalSyncFailed') || 'External sync failed'}
              </Badge>
            )}
            <small className="text-muted">#{item.id}</small>
          </div>

          {/* Subject */}
          <h5 className="mb-2">{item.subject}</h5>

          {/* Body Preview */}
          {item.body && (
            <p className="text-muted mb-2" style={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical'
            }}>
              {item.body}
            </p>
          )}

          {/* Metadata */}
          <div className="text-muted">
            <small>
              <i className="bi bi-person me-1" />
              {item.sender_email}
            </small>
            <span className="mx-2">•</span>
            <small>
              <i className="bi bi-clock me-1" />
              {formatRelativeDate(item.received_at, i18n.language)}
            </small>
          </div>
        </div>

        {/* Actions */}
        <div className="ms-3 d-flex flex-column gap-2">
          <Button
            variant="outline-primary"
            size="sm"
            onClick={onView}
          >
            <i className="bi bi-eye me-1" />
            {t('common.view') || 'View'}
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={onAssign}
          >
            <i className="bi bi-kanban me-1" />
            {t('standbyQueue.assign') || 'Assign'}
          </Button>
          {item.external_sync_failed && (
            <Button
              variant="warning"
              size="sm"
              onClick={onRetry}
            >
              <i className="bi bi-arrow-repeat" />
            </Button>
          )}
          <Button
            variant="outline-danger"
            size="sm"
            onClick={onDiscard}
          >
            <i className="bi bi-trash" />
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default QueueItemCard;
