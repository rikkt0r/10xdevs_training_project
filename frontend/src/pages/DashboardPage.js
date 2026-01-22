import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Row, Col, ListGroup } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import * as dashboardService from '../services/dashboardService';
import ManagerLayout from '../components/layout/ManagerLayout';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import Alert from '../components/common/Alert';
import Spinner from '../components/common/Spinner';
import EmptyState from '../components/common/EmptyState';
import { formatRelativeDate } from '../utils/dateUtils';
import { getStateBadgeVariant, getStateLabel } from '../utils/ticketUtils';

const DashboardPage = () => {
  const { t, i18n } = useTranslation();

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

  const breadcrumbs = [
    { label: t('nav.dashboard') || 'Dashboard' }
  ];

  if (loading) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Spinner fullPage message={t('common.loading')} />
      </ManagerLayout>
    );
  }

  if (error) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Alert variant="danger">{error}</Alert>
      </ManagerLayout>
    );
  }

  return (
    <ManagerLayout breadcrumbs={breadcrumbs}>
      <div className="mb-4">
        <h1>{t('dashboard.title')}</h1>
      </div>

      {/* Statistics Cards */}
      <Row className="mb-4">
        <Col md={6} lg={3} className="mb-3">
          <Card className="h-100">
            <h6 className="text-muted mb-2">{t('dashboard.totalBoards')}</h6>
            <h2 className="mb-0">{stats.boards_count}</h2>
            <small className="text-success">
              {stats.active_boards_count} {t('dashboard.active')}
            </small>
          </Card>
        </Col>

        <Col md={6} lg={3} className="mb-3">
          <Card className="h-100">
            <h6 className="text-muted mb-2">{t('dashboard.standbyQueue')}</h6>
            <h2 className="mb-0">{stats.standby_queue_count}</h2>
            <small className="text-muted">{t('dashboard.itemsWaiting')}</small>
          </Card>
        </Col>

        <Col md={6} lg={3} className="mb-3">
          <Card className="h-100">
            <h6 className="text-muted mb-2">{t('dashboard.newTickets')}</h6>
            <h2 className="mb-0">{stats.tickets_by_state.new}</h2>
            <small className="text-muted">{t('dashboard.requiresAction')}</small>
          </Card>
        </Col>

        <Col md={6} lg={3} className="mb-3">
          <Card className="h-100">
            <h6 className="text-muted mb-2">{t('dashboard.inProgress')}</h6>
            <h2 className="mb-0">{stats.tickets_by_state.in_progress}</h2>
            <small className="text-muted">{t('dashboard.beingWorkedOn')}</small>
          </Card>
        </Col>
      </Row>

      {/* Ticket State Summary and Recent Activity */}
      <Row className="mb-4">
        <Col md={6} className="mb-3">
          <Card title={t('dashboard.ticketsByState')}>
            <ListGroup variant="flush">
              <ListGroup.Item className="d-flex justify-content-between align-items-center">
                <span>
                  <Badge variant="primary" className="me-2">
                    {getStateLabel('new', t)}
                  </Badge>
                </span>
                <strong>{stats.tickets_by_state.new}</strong>
              </ListGroup.Item>
              <ListGroup.Item className="d-flex justify-content-between align-items-center">
                <span>
                  <Badge variant="warning" className="me-2">
                    {getStateLabel('in_progress', t)}
                  </Badge>
                </span>
                <strong>{stats.tickets_by_state.in_progress}</strong>
              </ListGroup.Item>
              <ListGroup.Item className="d-flex justify-content-between align-items-center">
                <span>
                  <Badge variant="success" className="me-2">
                    {getStateLabel('closed', t)}
                  </Badge>
                </span>
                <strong>{stats.tickets_by_state.closed}</strong>
              </ListGroup.Item>
              <ListGroup.Item className="d-flex justify-content-between align-items-center">
                <span>
                  <Badge variant="danger" className="me-2">
                    {getStateLabel('rejected', t)}
                  </Badge>
                </span>
                <strong>{stats.tickets_by_state.rejected}</strong>
              </ListGroup.Item>
            </ListGroup>
          </Card>
        </Col>

        <Col md={6} className="mb-3">
          <Card title={t('dashboard.recentActivity')}>
            <div className="mb-3">
              <h6 className="text-muted">{t('dashboard.createdToday')}</h6>
              <h3 className="text-primary">{stats.recent_activity.tickets_created_today}</h3>
            </div>
            <div>
              <h6 className="text-muted">{t('dashboard.createdThisWeek')}</h6>
              <h3 className="text-info">{stats.recent_activity.tickets_created_this_week}</h3>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Row className="mb-4">
        <Col>
          <Card title={t('dashboard.quickActions')}>
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
              <Button variant="secondary" as={Link} to="/settings">
                {t('dashboard.settings')}
              </Button>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Recent Tickets */}
      <Row>
        <Col>
          <Card
            header={
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">{t('dashboard.recentTickets')}</h5>
                <Button variant="link" size="sm" as={Link} to="/tickets" className="text-decoration-none">
                  {t('dashboard.viewAll')}
                </Button>
              </div>
            }
          >
            {recentTickets.length === 0 ? (
              <EmptyState
                icon="bi-inbox"
                title={t('dashboard.noRecentTickets')}
                message={t('dashboard.noRecentTicketsMessage') || 'No recent tickets to display'}
              />
            ) : (
              <ListGroup variant="flush">
                {recentTickets.map((ticket) => (
                  <ListGroup.Item
                    key={ticket.id}
                    className="d-flex justify-content-between align-items-start"
                  >
                    <div className="flex-grow-1">
                      <div className="d-flex align-items-center mb-1">
                        <Badge variant={getStateBadgeVariant(ticket.state)} className="me-2">
                          {getStateLabel(ticket.state, t)}
                        </Badge>
                        <h6 className="mb-0">{ticket.title}</h6>
                      </div>
                      <small className="text-muted">
                        {ticket.board.name} • {formatRelativeDate(ticket.created_at, i18n.language)}
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
          </Card>
        </Col>
      </Row>
    </ManagerLayout>
  );
};

export default DashboardPage;
