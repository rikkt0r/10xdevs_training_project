import React from 'react';
import { useTranslation } from 'react-i18next';
import Card from '../common/Card';
import Badge from '../common/Badge';
import Button from '../common/Button';

/**
 * InboxCard component
 * Card view for inbox summary
 */
const InboxCard = ({ inbox, onEdit, onTest, onDelete, testing = false }) => {
  const { t } = useTranslation();

  return (
    <Card className="h-100">
      <div className="d-flex justify-content-between align-items-start mb-3">
        <div className="flex-grow-1">
          <h5 className="mb-2">
            <i className="bi bi-envelope me-2" />
            {inbox.imap_username}
          </h5>
          <div className="text-muted mb-2">
            <small>
              <i className="bi bi-server me-1" />
              {inbox.imap_host}:{inbox.imap_port}
            </small>
          </div>
          {inbox.board && (
            <Badge variant="info">
              <i className="bi bi-kanban me-1" />
              {inbox.board.name}
            </Badge>
          )}
        </div>
      </div>

      <hr />

      <div className="mb-3">
        <strong className="d-block mb-1">{t('settings.pollingInterval') || 'Polling Interval'}:</strong>
        <span className="text-muted">
          {inbox.polling_interval ? `${inbox.polling_interval} ${t('settings.seconds') || 'seconds'}` : '-'}
        </span>
      </div>

      {inbox.last_checked_at && (
        <div className="mb-3">
          <strong className="d-block mb-1">{t('settings.lastChecked') || 'Last Checked'}:</strong>
          <span className="text-muted">
            {new Date(inbox.last_checked_at).toLocaleString()}
          </span>
        </div>
      )}

      <div className="d-grid gap-2 mt-3">
        <Button
          variant="primary"
          size="sm"
          onClick={onTest}
          loading={testing}
        >
          <i className="bi bi-plug me-2" />
          {t('settings.testConnection') || 'Test Connection'}
        </Button>
        <div className="d-flex gap-2">
          <Button
            variant="outline-secondary"
            size="sm"
            onClick={onEdit}
            fullWidth
          >
            <i className="bi bi-pencil me-1" />
            {t('common.edit') || 'Edit'}
          </Button>
          <Button
            variant="outline-danger"
            size="sm"
            onClick={onDelete}
            fullWidth
          >
            <i className="bi bi-trash me-1" />
            {t('common.delete') || 'Delete'}
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default InboxCard;
