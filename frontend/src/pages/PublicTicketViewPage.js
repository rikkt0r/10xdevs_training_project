import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Alert, Container, Row, Col, Spinner, Badge, ListGroup, Button } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import * as publicService from '../services/publicService';

const PublicTicketViewPage = () => {
  const { t } = useTranslation();
  const { uuid } = useParams();

  const [loading, setLoading] = useState(true);
  const [ticket, setTicket] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadTicket = async () => {
      try {
        setLoading(true);
        const response = await publicService.getPublicTicket(uuid);
        setTicket(response.data.data);
        setError(null);
      } catch (err) {
        if (err.response?.status === 404) {
          setError({
            message: t('public.errors.ticketNotFound'),
          });
        } else {
          setError({
            message: t('public.errors.loadTicketFailed'),
          });
        }
      } finally {
        setLoading(false);
      }
    };

    loadTicket();
  }, [uuid, t]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getStateBadgeVariant = (state) => {
    switch (state) {
      case 'new':
        return 'primary';
      case 'in_progress':
        return 'warning';
      case 'closed':
        return 'success';
      case 'rejected':
        return 'danger';
      default:
        return 'secondary';
    }
  };

  const getStateLabel = (state) => {
    switch (state) {
      case 'new':
        return t('tickets.new');
      case 'in_progress':
        return t('tickets.inProgress');
      case 'closed':
        return t('tickets.closed');
      case 'rejected':
        return t('tickets.rejected');
      default:
        return state;
    }
  };

  if (loading) {
    return (
      <Container>
        <Row className="justify-content-center mt-5">
          <Col md={10} lg={8}>
            <div className="text-center">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">{t('common.loading')}</span>
              </Spinner>
            </div>
          </Col>
        </Row>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Row className="justify-content-center mt-5">
          <Col md={10} lg={8}>
            <Card>
              <Card.Body>
                <h2 className="text-center mb-4">{t('public.ticketNotFound')}</h2>
                <Alert variant="danger">{error.message}</Alert>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  // Handle external tickets (redirect to external platform)
  if (ticket.external_url) {
    return (
      <Container>
        <Row className="justify-content-center mt-5">
          <Col md={10} lg={8}>
            <Card>
              <Card.Body>
                <h2 className="text-center mb-4">{t('public.externalTicket')}</h2>
                <Alert variant="info">
                  <p>{t('public.externalTicketMessage')}</p>
                  <p className="mb-0">
                    <strong>{t('public.platform')}:</strong>{' '}
                    {ticket.platform_type === 'jira' ? 'Jira' : 'Trello'}
                  </p>
                </Alert>

                <Card className="mb-3">
                  <Card.Body>
                    <h5>{ticket.title}</h5>
                    <p className="text-muted mb-2">
                      <small>
                        {t('public.board')}: {ticket.board_name}
                      </small>
                    </p>
                    <p className="text-muted mb-0">
                      <small>
                        {t('public.created')}: {formatDate(ticket.created_at)}
                      </small>
                    </p>
                  </Card.Body>
                </Card>

                <div className="text-center">
                  <Button
                    variant="primary"
                    href={ticket.external_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {t('public.viewOnPlatform')}
                  </Button>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  // Handle internal tickets
  return (
    <Container>
      <Row className="justify-content-center mt-5">
        <Col md={10} lg={8}>
          <Card className="mb-3">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start mb-3">
                <h2>{ticket.title}</h2>
                <Badge bg={getStateBadgeVariant(ticket.state)} className="ms-2">
                  {getStateLabel(ticket.state)}
                </Badge>
              </div>

              <p className="text-muted mb-3">
                <small>
                  {t('public.board')}: {ticket.board_name} | {t('public.created')}:{' '}
                  {formatDate(ticket.created_at)}
                  {ticket.updated_at !== ticket.created_at && (
                    <>
                      {' '}
                      | {t('public.updated')}: {formatDate(ticket.updated_at)}
                    </>
                  )}
                </small>
              </p>

              <Card className="bg-light">
                <Card.Body>
                  <h6>{t('public.description')}</h6>
                  <p style={{ whiteSpace: 'pre-wrap' }}>{ticket.description}</p>
                </Card.Body>
              </Card>
            </Card.Body>
          </Card>

          {ticket.status_changes && ticket.status_changes.length > 0 && (
            <Card>
              <Card.Body>
                <h5 className="mb-3">{t('public.statusHistory')}</h5>
                <ListGroup variant="flush">
                  {ticket.status_changes.map((change, index) => (
                    <ListGroup.Item key={index}>
                      <div className="d-flex justify-content-between align-items-start">
                        <div>
                          <Badge bg={getStateBadgeVariant(change.previous_state)} className="me-2">
                            {getStateLabel(change.previous_state)}
                          </Badge>
                          <span className="mx-2">→</span>
                          <Badge bg={getStateBadgeVariant(change.new_state)}>
                            {getStateLabel(change.new_state)}
                          </Badge>
                        </div>
                        <small className="text-muted">{formatDate(change.created_at)}</small>
                      </div>
                      {change.comment && (
                        <div className="mt-2">
                          <small>
                            <strong>{t('public.comment')}:</strong> {change.comment}
                          </small>
                        </div>
                      )}
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              </Card.Body>
            </Card>
          )}

          <div className="text-center mt-3 mb-5">
            <small className="text-muted">
              {t('public.ticketId')}: {ticket.uuid}
            </small>
          </div>
        </Col>
      </Row>
    </Container>
  );
};

export default PublicTicketViewPage;
