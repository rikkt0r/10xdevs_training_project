import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Row, Col, Nav, Tab } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { fetchBoard } from '../store/slices/boardsSlice';
import { fetchBoardTickets } from '../store/slices/ticketsSlice';
import ManagerLayout from '../components/layout/ManagerLayout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Spinner from '../components/common/Spinner';
import Alert from '../components/common/Alert';
import EmptyState from '../components/common/EmptyState';

const BoardDetailPage = () => {
  const { t } = useTranslation();
  const { id: boardId } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { currentBoard, loading, error } = useSelector((state) => state.boards);
  const { tickets } = useSelector((state) => state.tickets);

  const [activeTab, setActiveTab] = useState('tickets');

  useEffect(() => {
    if (boardId) {
      dispatch(fetchBoard(boardId));
      dispatch(fetchBoardTickets({ boardId }));
    }
  }, [dispatch, boardId]);

  const breadcrumbs = [
    { label: t('nav.dashboard') || 'Dashboard', path: '/dashboard' },
    { label: t('nav.boards') || 'Boards', path: '/boards' },
    { label: currentBoard?.name || 'Board Details' }
  ];

  const handleEditBoard = () => {
    navigate(`/boards/${boardId}/edit`);
  };

  if (loading && !currentBoard) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Spinner fullPage message={t('common.loading')} />
      </ManagerLayout>
    );
  }

  if (error) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Alert variant="danger">{error.message || t('boards.errors.loadFailed')}</Alert>
      </ManagerLayout>
    );
  }

  if (!currentBoard) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Alert variant="warning">{t('boards.notFound') || 'Board not found'}</Alert>
      </ManagerLayout>
    );
  }

  return (
    <ManagerLayout breadcrumbs={breadcrumbs}>
      {/* Board Header */}
      <div className="d-flex justify-content-between align-items-start mb-4">
        <div>
          <div className="d-flex align-items-center gap-2 mb-2">
            <h1 className="mb-0">{currentBoard.name}</h1>
            {currentBoard.archived && (
              <Badge variant="secondary">{t('boards.archived') || 'Archived'}</Badge>
            )}
            {currentBoard.external_platform && (
              <Badge variant="info">
                {currentBoard.external_platform === 'jira' ? 'Jira' : 'Trello'}
              </Badge>
            )}
          </div>
          {currentBoard.greeting && (
            <p className="text-muted mb-0">{currentBoard.greeting}</p>
          )}
        </div>
        <Button variant="outline-primary" onClick={handleEditBoard}>
          <i className="bi bi-pencil me-2" />
          {t('boards.edit') || 'Edit'}
        </Button>
      </div>

      {/* Stats Cards */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="h-100">
            <h6 className="text-muted mb-2">{t('tickets.new') || 'New'}</h6>
            <h2 className="mb-0 text-primary">{currentBoard.ticket_counts?.new || 0}</h2>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="h-100">
            <h6 className="text-muted mb-2">{t('tickets.inProgress') || 'In Progress'}</h6>
            <h2 className="mb-0 text-warning">{currentBoard.ticket_counts?.in_progress || 0}</h2>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="h-100">
            <h6 className="text-muted mb-2">{t('tickets.waiting') || 'Waiting'}</h6>
            <h2 className="mb-0 text-info">{currentBoard.ticket_counts?.waiting || 0}</h2>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="h-100">
            <h6 className="text-muted mb-2">{t('tickets.resolved') || 'Resolved'}</h6>
            <h2 className="mb-0 text-success">{currentBoard.ticket_counts?.resolved || 0}</h2>
          </Card>
        </Col>
      </Row>

      {/* Tabs */}
      <Card>
        <Tab.Container activeKey={activeTab} onSelect={(k) => setActiveTab(k)}>
          <Nav variant="tabs">
            <Nav.Item>
              <Nav.Link eventKey="tickets">
                <i className="bi bi-ticket me-2" />
                {t('boards.tabs.tickets') || 'Tickets'}
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="keywords">
                <i className="bi bi-tags me-2" />
                {t('boards.tabs.keywords') || 'Keywords'}
              </Nav.Link>
            </Nav.Item>
            {currentBoard.external_platform && (
              <Nav.Item>
                <Nav.Link eventKey="external">
                  <i className="bi bi-box-arrow-up-right me-2" />
                  {t('boards.tabs.externalTickets') || 'External Tickets'}
                </Nav.Link>
              </Nav.Item>
            )}
            <Nav.Item>
              <Nav.Link eventKey="settings">
                <i className="bi bi-gear me-2" />
                {t('boards.tabs.settings') || 'Settings'}
              </Nav.Link>
            </Nav.Item>
          </Nav>

          <div className="p-4">
            <Tab.Content>
              <Tab.Pane eventKey="tickets">
                {tickets.length === 0 ? (
                  <EmptyState
                    icon="bi-inbox"
                    title={t('tickets.noTickets') || 'No tickets'}
                    message={t('tickets.noTicketsMessage') || 'No tickets found for this board'}
                  />
                ) : (
                  <div>
                    <p className="text-muted">
                      {t('boards.ticketsCount', { count: tickets.length }) || `${tickets.length} tickets`}
                    </p>
                    {/* Ticket list will go here */}
                  </div>
                )}
              </Tab.Pane>

              <Tab.Pane eventKey="keywords">
                <EmptyState
                  icon="bi-tags"
                  title={t('boards.keywords.title') || 'Keywords'}
                  message={t('boards.keywords.description') || 'Keywords help route incoming emails to this board'}
                />
                {/* Keyword management will go here */}
              </Tab.Pane>

              {currentBoard.external_platform && (
                <Tab.Pane eventKey="external">
                  <EmptyState
                    icon="bi-box-arrow-up-right"
                    title={t('boards.external.title') || 'External Platform'}
                    message={t('boards.external.description') || 'Tickets synced with external platform'}
                  />
                  {/* External tickets will go here */}
                </Tab.Pane>
              )}

              <Tab.Pane eventKey="settings">
                <div>
                  <h5 className="mb-3">{t('boards.settings.title') || 'Board Settings'}</h5>
                  <div className="mb-3">
                    <strong>{t('boards.name') || 'Name'}:</strong> {currentBoard.name}
                  </div>
                  <div className="mb-3">
                    <strong>{t('boards.greeting') || 'Greeting'}:</strong>{' '}
                    {currentBoard.greeting || '-'}
                  </div>
                <div className="mb-3">
                    <strong>{t('boards.unique_name')}:</strong>{' '}
                    {currentBoard.unique_name || '-'}
                  </div>
                  <div className="mb-3">
                    <strong>{t('boards.externalPlatform') || 'External Platform'}:</strong>{' '}
                    {currentBoard.external_platform ? (
                      <Badge variant="info">
                        {currentBoard.external_platform === 'jira' ? 'Jira' : 'Trello'}
                      </Badge>
                    ) : (
                      '-'
                    )}
                  </div>
                </div>
              </Tab.Pane>
            </Tab.Content>
          </div>
        </Tab.Container>
      </Card>
    </ManagerLayout>
  );
};

export default BoardDetailPage;
