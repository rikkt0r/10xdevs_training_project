import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Row, Col, Table } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { fetchBoards, deleteBoard, archiveBoard } from '../store/slices/boardsSlice';
import ManagerLayout from '../components/layout/ManagerLayout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Spinner from '../components/common/Spinner';
import EmptyState from '../components/common/EmptyState';
import Alert from '../components/common/Alert';
import ConfirmModal from '../components/common/ConfirmModal';
import Checkbox from '../components/common/Checkbox';

const BoardListPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { boards, loading, error } = useSelector((state) => state.boards);

  const [showArchived, setShowArchived] = useState(false);
  const [deleteModalShow, setDeleteModalShow] = useState(false);
  const [archiveModalShow, setArchiveModalShow] = useState(false);
  const [selectedBoard, setSelectedBoard] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    dispatch(fetchBoards());
  }, [dispatch]);

  const breadcrumbs = [
    { label: t('nav.dashboard') || 'Dashboard', path: '/dashboard' },
    { label: t('nav.boards') || 'Boards' }
  ];

  const filteredBoards = boards.filter(board =>
    showArchived ? true : !board.archived
  );

  const handleViewBoard = (boardId) => {
    navigate(`/boards/${boardId}`);
  };

  const handleCreateBoard = () => {
    navigate('/boards/new');
  };

  const handleEditBoard = (boardId) => {
    navigate(`/boards/${boardId}/edit`);
  };

  const handleArchiveBoard = async () => {
    if (!selectedBoard) return;

    setActionLoading(true);
    try {
      await dispatch(archiveBoard(selectedBoard.id)).unwrap();
      setArchiveModalShow(false);
      setSelectedBoard(null);
    } catch (err) {
      console.error('Failed to archive board:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteBoard = async () => {
    if (!selectedBoard) return;

    setActionLoading(true);
    try {
      await dispatch(deleteBoard(selectedBoard.id)).unwrap();
      setDeleteModalShow(false);
      setSelectedBoard(null);
    } catch (err) {
      console.error('Failed to delete board:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const openArchiveModal = (board) => {
    setSelectedBoard(board);
    setArchiveModalShow(true);
  };

  const openDeleteModal = (board) => {
    setSelectedBoard(board);
    setDeleteModalShow(true);
  };

  if (loading && boards.length === 0) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Spinner fullPage message={t('common.loading')} />
      </ManagerLayout>
    );
  }

  return (
    <ManagerLayout breadcrumbs={breadcrumbs}>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>{t('boards.title') || 'Boards'}</h1>
        <Button variant="primary" onClick={handleCreateBoard}>
          <i className="bi bi-plus-circle me-2" />
          {t('boards.createBoard') || 'Create Board'}
        </Button>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error.message || t('boards.errors.loadFailed')}
        </Alert>
      )}

      <Row className="mb-4">
        <Col>
          <Card>
            <div className="mb-3">
              <Checkbox
                id="showArchived"
                label={t('boards.showArchived') || 'Show archived boards'}
                checked={showArchived}
                onChange={(e) => setShowArchived(e.target.checked)}
              />
            </div>

            {filteredBoards.length === 0 ? (
              <EmptyState
                icon="bi-kanban"
                title={showArchived ? t('boards.noArchivedBoards') : t('boards.noBoards')}
                message={showArchived ? '' : t('boards.noBoardsMessage') || 'Create your first board to get started'}
                actionLabel={!showArchived ? t('boards.createBoard') : undefined}
                onAction={!showArchived ? handleCreateBoard : undefined}
              />
            ) : (
              <Table responsive hover>
                <thead>
                  <tr>
                    <th>{t('boards.name') || 'Name'}</th>
                    <th>{t('boards.greeting') || 'Greeting'}</th>
                    <th>{t('boards.externalPlatform') || 'External Platform'}</th>
                    <th className="text-center">{t('boards.ticketCounts') || 'Tickets'}</th>
                    <th>{t('boards.status') || 'Status'}</th>
                    <th className="text-end">{t('common.actions') || 'Actions'}</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredBoards.map((board) => (
                    <tr key={board.id}>
                      <td>
                        <strong>{board.name}</strong>
                      </td>
                      <td>
                        <small className="text-muted">{board.greeting || '-'}</small>
                      </td>
                      <td>
                        {board.external_platform ? (
                          <Badge variant="info">
                            {board.external_platform === 'jira' ? 'Jira' : 'Trello'}
                          </Badge>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                      <td className="text-center">
                        <div className="d-flex gap-2 justify-content-center">
                          <Badge variant="primary">{board.ticket_counts?.new || 0}</Badge>
                          <Badge variant="warning">{board.ticket_counts?.in_progress || 0}</Badge>
                          <Badge variant="success">{board.ticket_counts?.closed || 0}</Badge>
                        </div>
                      </td>
                      <td>
                        {board.archived ? (
                          <Badge variant="secondary">{t('boards.archived') || 'Archived'}</Badge>
                        ) : (
                          <Badge variant="success">{t('boards.active') || 'Active'}</Badge>
                        )}
                      </td>
                      <td className="text-end">
                        <div className="d-flex gap-2 justify-content-end">
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => handleViewBoard(board.id)}
                          >
                            <i className="bi bi-eye" />
                          </Button>
                          {!board.archived && (
                            <>
                              <Button
                                variant="outline-secondary"
                                size="sm"
                                onClick={() => handleEditBoard(board.id)}
                              >
                                <i className="bi bi-pencil" />
                              </Button>
                              <Button
                                variant="outline-warning"
                                size="sm"
                                onClick={() => openArchiveModal(board)}
                              >
                                <i className="bi bi-archive" />
                              </Button>
                            </>
                          )}
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => openDeleteModal(board)}
                          >
                            <i className="bi bi-trash" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            )}
          </Card>
        </Col>
      </Row>

      {/* Archive Confirmation Modal */}
      <ConfirmModal
        show={archiveModalShow}
        onHide={() => setArchiveModalShow(false)}
        title={t('boards.archiveBoard') || 'Archive Board'}
        message={t('boards.archiveConfirm', { name: selectedBoard?.name }) || `Are you sure you want to archive "${selectedBoard?.name}"?`}
        confirmLabel={t('boards.archive') || 'Archive'}
        variant="warning"
        onConfirm={handleArchiveBoard}
        loading={actionLoading}
      />

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        show={deleteModalShow}
        onHide={() => setDeleteModalShow(false)}
        title={t('boards.deleteBoard') || 'Delete Board'}
        message={t('boards.deleteConfirm', { name: selectedBoard?.name }) || `Are you sure you want to delete "${selectedBoard?.name}"? This action cannot be undone.`}
        confirmLabel={t('boards.delete') || 'Delete'}
        variant="danger"
        onConfirm={handleDeleteBoard}
        loading={actionLoading}
      />
    </ManagerLayout>
  );
};

export default BoardListPage;
