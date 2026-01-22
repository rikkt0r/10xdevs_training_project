import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, Row, Col, ListGroup, Badge, Alert, Spinner, Button } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import { useDispatch } from 'react-redux';
import * as dashboardService from '../services/dashboardService';
import { logout } from '../store/slices/authSlice';

const DashboardPage = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();

  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [recentTickets, setRecentTickets] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [statsResponse, ticketsResponse] = await Promise.all([
          dashboardService.getDashboardStats(),
          dashboardService.getRecentTickets(10),
        ]);

        setStats(statsResponse.data.data);
        setRecentTickets(ticketsResponse.data.data);
      } catch (err) {
        setError(err.response?.data?.error?.message || t('dashboard.errors.loadFailed'));
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [t]);

  const handleLogout = () => {
    dispatch(logout());
  };

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
      <div className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">{t('common.loading')}</span>
        </Spinner>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-5">
        <Alert variant="danger">{error}</Alert>
      </div>
    );
  }

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>{t('dashboard.title')}</h1>
        <Button variant="outline-secondary" size="sm" onClick={handleLogout}>
          {t('auth.logout')}
        </Button>
      </div>

      {/* Statistics Cards */}
      <Row className="mb-4">
        <Col md={6} lg={3} className="mb-3">
          <Card className="h-100">
            <Card.Body>
              <h6 className="text-muted mb-2">{t('dashboard.totalBoards')}</h6>
              <h2 className="mb-0">{stats.boards_count}</h2>
              <small className="text-success">
                {stats.active_boards_count} {t('dashboard.active')}
              </small>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6} lg={3} className="mb-3">
          <Card className="h-100">
            <Card.Body>
              <h6 className="text-muted mb-2">{t('dashboard.standbyQueue')}</h6>
              <h2 className="mb-0">{stats.standby_queue_count}</h2>
              <small className="text-muted">{t('dashboard.itemsWaiting')}</small>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6} lg={3} className="mb-3">
          <Card className="h-100">
            <Card.Body>
              <h6 className="text-muted mb-2">{t('dashboard.newTickets')}</h6>
              <h2 className="mb-0">{stats.tickets_by_state.new}</h2>
              <small className="text-muted">{t('dashboard.requiresAction')}</small>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6} lg={3} className="mb-3">
          <Card className="h-100">
            <Card.Body>
              <h6 className="text-muted mb-2">{t('dashboard.inProgress')}</h6>
              <h2 className="mb-0">{stats.tickets_by_state.in_progress}</h2>
              <small className="text-muted">{t('dashboard.beingWorkedOn')}</small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Ticket State Summary and Recent Activity */}
      <Row className="mb-4">
        <Col md={6} className="mb-3">
          <Card>
            <Card.Header>
              <h5 className="mb-0">{t('dashboard.ticketsByState')}</h5>
            </Card.Header>
            <Card.Body>
              <ListGroup variant="flush">
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>
                    <Badge bg="primary" className="me-2">
                      {getStateLabel('new')}
                    </Badge>
                  </span>
                  <strong>{stats.tickets_by_state.new}</strong>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>
                    <Badge bg="warning" className="me-2">
                      {getStateLabel('in_progress')}
                    </Badge>
                  </span>
                  <strong>{stats.tickets_by_state.in_progress}</strong>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>
                    <Badge bg="success" className="me-2">
                      {getStateLabel('closed')}
                    </Badge>
                  </span>
                  <strong>{stats.tickets_by_state.closed}</strong>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>
                    <Badge bg="danger" className="me-2">
                      {getStateLabel('rejected')}
                    </Badge>
                  </span>
                  <strong>{stats.tickets_by_state.rejected}</strong>
                </ListGroup.Item>
              </ListGroup>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6} className="mb-3">
          <Card>
            <Card.Header>
              <h5 className="mb-0">{t('dashboard.recentActivity')}</h5>
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <h6 className="text-muted">{t('dashboard.createdToday')}</h6>
                <h3 className="text-primary">{stats.recent_activity.tickets_created_today}</h3>
              </div>
              <div>
                <h6 className="text-muted">{t('dashboard.createdThisWeek')}</h6>
                <h3 className="text-info">{stats.recent_activity.tickets_created_this_week}</h3>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">{t('dashboard.quickActions')}</h5>
            </Card.Header>
            <Card.Body>
              <div className="d-flex gap-2 flex-wrap">
                <Button variant="primary" as={Link} to="/boards">
                  {t('dashboard.manageBoards')}
                </Button>
                <Button variant="info" as={Link} to="/tickets">
                  {t('dashboard.viewAllTickets')}
                </Button>
                {stats.standby_queue_count > 0 && (
                  <Button variant="warning" as={Link} to="/standby-queue">
                    {t('dashboard.processStandbyQueue')} ({stats.standby_queue_count})
                  </Button>
                )}
                <Button variant="secondary" as={Link} to="/inboxes">
                  {t('dashboard.manageInboxes')}
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Recent Tickets */}
      <Row>
        <Col>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">{t('dashboard.recentTickets')}</h5>
              <Button variant="link" size="sm" as={Link} to="/tickets">
                {t('dashboard.viewAll')}
              </Button>
            </Card.Header>
            <Card.Body>
              {recentTickets.length === 0 ? (
                <p className="text-muted text-center mb-0">{t('dashboard.noRecentTickets')}</p>
              ) : (
                <ListGroup variant="flush">
                  {recentTickets.map((ticket) => (
                    <ListGroup.Item
                      key={ticket.id}
                      className="d-flex justify-content-between align-items-start"
                    >
                      <div className="flex-grow-1">
                        <div className="d-flex align-items-center mb-1">
                          <Badge bg={getStateBadgeVariant(ticket.state)} className="me-2">
                            {getStateLabel(ticket.state)}
                          </Badge>
                          <h6 className="mb-0">{ticket.title}</h6>
                        </div>
                        <small className="text-muted">
                          {ticket.board.name} • {formatDate(ticket.created_at)}
                        </small>
                      </div>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        as={Link}
                        to={`/ticket/${ticket.uuid}`}
                      >
                        {t('dashboard.view')}
                      </Button>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;
