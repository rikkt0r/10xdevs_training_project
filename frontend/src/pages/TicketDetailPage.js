import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Row, Col } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { fetchTicket, fetchTicketHistory, changeTicketState } from '../store/slices/ticketsSlice';
import ManagerLayout from '../components/layout/ManagerLayout';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import Alert from '../components/common/Alert';
import Timeline from '../components/common/Timeline';
import { formatDateTime, formatRelativeDate } from '../utils/dateUtils';
import { getStateBadgeVariant, getStateLabel, getValidTransitions, getSourceLabel, getSourceIcon } from '../utils/ticketUtils';
import StateChangeModal from '../components/tickets/StateChangeModal';

const TicketDetailPage = () => {
  const { t, i18n } = useTranslation();
  const { ticketId } = useParams();
  const dispatch = useDispatch();
  const { currentTicket, ticketHistory, loading, error } = useSelector((state) => state.tickets);

  const [stateChangeModalShow, setStateChangeModalShow] = useState(false);
  const [selectedNewState, setSelectedNewState] = useState(null);

  useEffect(() => {
    if (ticketId) {
      dispatch(fetchTicket(ticketId));
      dispatch(fetchTicketHistory(ticketId));
    }
  }, [dispatch, ticketId]);

  const breadcrumbs = [
    { label: t('nav.dashboard') || 'Dashboard', path: '/dashboard' },
    { label: t('nav.boards') || 'Boards', path: '/boards' },
    ...(currentTicket?.board ? [{ label: currentTicket.board.name, path: `/boards/${currentTicket.board.id}` }] : []),
    { label: `#${currentTicket?.id || ticketId}` }
  ];

  const handleStateChange = (newState) => {
    setSelectedNewState(newState);
    setStateChangeModalShow(true);
  };

  const handleStateChangeConfirm = async (comment) => {
    try {
      await dispatch(changeTicketState({
        ticketId: currentTicket.id,
        newState: selectedNewState,
        comment
      })).unwrap();
      setStateChangeModalShow(false);
      setSelectedNewState(null);
      // Refresh history after state change
      dispatch(fetchTicketHistory(ticketId));
    } catch (err) {
      console.error('Failed to change ticket state:', err);
    }
  };

  const validTransitions = currentTicket ? getValidTransitions(currentTicket.state) : [];

  const timelineItems = ticketHistory.map((history) => ({
    title: `${getStateLabel(history.old_state, t)} → ${getStateLabel(history.new_state, t)}`,
    description: history.comment,
    date: history.changed_at,
    variant: getStateBadgeVariant(history.new_state),
    badgeVariant: getStateBadgeVariant(history.new_state),
    badge: getStateLabel(history.new_state, t),
    user: history.changed_by?.name || history.changed_by?.email
  }));

  if (loading && !currentTicket) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Spinner fullPage message={t('common.loading')} />
      </ManagerLayout>
    );
  }

  if (error) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Alert variant="danger">{error.message || t('tickets.errors.loadFailed')}</Alert>
      </ManagerLayout>
    );
  }

  if (!currentTicket) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Alert variant="warning">{t('tickets.notFound') || 'Ticket not found'}</Alert>
      </ManagerLayout>
    );
  }

  return (
    <ManagerLayout breadcrumbs={breadcrumbs}>
      <Row className="mb-4">
        <Col lg={8}>
          {/* Ticket Header */}
          <Card className="mb-4">
            <div className="d-flex justify-content-between align-items-start mb-3">
              <div>
                <div className="d-flex align-items-center gap-2 mb-2">
                  <h2 className="mb-0">{currentTicket.title}</h2>
                  <Badge variant={getStateBadgeVariant(currentTicket.state)}>
                    {getStateLabel(currentTicket.state, t)}
                  </Badge>
                </div>
                <div className="text-muted">
                  <small>
                    <i className="bi bi-hash me-1" />
                    {currentTicket.id}
                  </small>
                  <span className="mx-2">•</span>
                  <small>
                    <i className="bi bi-clock me-1" />
                    {formatRelativeDate(currentTicket.created_at, i18n.language)}
                  </small>
                  <span className="mx-2">•</span>
                  <small>
                    <i className={`${getSourceIcon(currentTicket.source)} me-1`} />
                    {getSourceLabel(currentTicket.source, t)}
                  </small>
                </div>
              </div>
              <Button
                variant="outline-secondary"
                size="sm"
                as={Link}
                to={`/ticket/${currentTicket.uuid}`}
                target="_blank"
              >
                <i className="bi bi-box-arrow-up-right me-2" />
                {t('tickets.viewPublic') || 'Public View'}
              </Button>
            </div>

            <hr />

            {/* Creator Info */}
            <div className="mb-3">
              <strong>{t('tickets.submittedBy') || 'Submitted by'}:</strong>
              <div className="text-muted">
                <i className="bi bi-person me-2" />
                {currentTicket.creator_email}
              </div>
            </div>

            {/* Board Info */}
            <div className="mb-3">
              <strong>{t('tickets.board') || 'Board'}:</strong>
              <div>
                <Link to={`/boards/${currentTicket.board.id}`}>
                  {currentTicket.board.name}
                </Link>
              </div>
            </div>

            <hr />

            {/* Description */}
            <div>
              <strong className="mb-2 d-block">{t('tickets.description') || 'Description'}:</strong>
              <div className="p-3 bg-light rounded">
                <pre className="mb-0" style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                  {currentTicket.description}
                </pre>
              </div>
            </div>
          </Card>

          {/* State Change Actions */}
          {validTransitions.length > 0 && (
            <Card title={t('tickets.changeState') || 'Change State'}>
              <div className="d-flex gap-2 flex-wrap">
                {validTransitions.map((state) => (
                  <Button
                    key={state}
                    variant={getStateBadgeVariant(state)}
                    onClick={() => handleStateChange(state)}
                  >
                    {getStateLabel(state, t)}
                  </Button>
                ))}
              </div>
            </Card>
          )}
        </Col>

        <Col lg={4}>
          {/* Timeline */}
          <Card title={t('tickets.history') || 'History'}>
            {timelineItems.length === 0 ? (
              <p className="text-muted text-center mb-0">
                {t('tickets.noHistory') || 'No status changes yet'}
              </p>
            ) : (
              <Timeline items={timelineItems} />
            )}
          </Card>
        </Col>
      </Row>

      {/* State Change Modal */}
      <StateChangeModal
        show={stateChangeModalShow}
        onHide={() => {
          setStateChangeModalShow(false);
          setSelectedNewState(null);
        }}
        currentState={currentTicket?.state}
        newState={selectedNewState}
        onConfirm={handleStateChangeConfirm}
      />
    </ManagerLayout>
  );
};

export default TicketDetailPage;
