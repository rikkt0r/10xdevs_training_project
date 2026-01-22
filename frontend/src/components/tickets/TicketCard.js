import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Card from '../common/Card';
import Badge from '../common/Badge';
import Button from '../common/Button';
import { formatRelativeDate } from '../../utils/dateUtils';
import { getStateBadgeVariant, getStateLabel, getSourceIcon, getSourceLabel } from '../../utils/ticketUtils';

/**
 * TicketCard component
 * Card view for ticket summary
 */
const TicketCard = ({ ticket, onStateChange }) => {
  const { t, i18n } = useTranslation();

  return (
    <Card className="mb-3">
      <div className="d-flex justify-content-between align-items-start">
        <div className="flex-grow-1">
          {/* Header */}
          <div className="d-flex align-items-center gap-2 mb-2">
            <Badge variant={getStateBadgeVariant(ticket.state)}>
              {getStateLabel(ticket.state, t)}
            </Badge>
            <small className="text-muted">
              <i className={`${getSourceIcon(ticket.source)} me-1`} />
              {getSourceLabel(ticket.source, t)}
            </small>
            <small className="text-muted">#{ticket.id}</small>
          </div>

          {/* Title */}
          <h5 className="mb-2">
            <Link to={`/tickets/${ticket.id}`} className="text-decoration-none text-dark">
              {ticket.title}
            </Link>
          </h5>

          {/* Description Preview */}
          {ticket.description && (
            <p className="text-muted mb-2" style={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical'
            }}>
              {ticket.description}
            </p>
          )}

          {/* Metadata */}
          <div className="text-muted">
            <small>
              <i className="bi bi-person me-1" />
              {ticket.creator_email}
            </small>
            <span className="mx-2">•</span>
            <small>
              <i className="bi bi-clock me-1" />
              {formatRelativeDate(ticket.created_at, i18n.language)}
            </small>
            {ticket.board && (
              <>
                <span className="mx-2">•</span>
                <small>
                  <i className="bi bi-kanban me-1" />
                  <Link to={`/boards/${ticket.board.id}`} className="text-muted">
                    {ticket.board.name}
                  </Link>
                </small>
              </>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="ms-3">
          <Button
            variant="outline-primary"
            size="sm"
            as={Link}
            to={`/tickets/${ticket.id}`}
          >
            <i className="bi bi-eye" />
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default TicketCard;
