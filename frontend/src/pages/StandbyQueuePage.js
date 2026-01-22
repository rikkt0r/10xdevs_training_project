import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Row, Col } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { fetchQueueItems, assignToBoard, retryExternal, discardItem } from '../store/slices/standbyQueueSlice';
import { fetchBoards } from '../store/slices/boardsSlice';
import ManagerLayout from '../components/layout/ManagerLayout';
import Card from '../components/common/Card';
import Spinner from '../components/common/Spinner';
import EmptyState from '../components/common/EmptyState';
import Alert from '../components/common/Alert';
import Pagination from '../components/common/Pagination';
import QueueItemCard from '../components/standbyQueue/QueueItemCard';
import AssignToBoardModal from '../components/standbyQueue/AssignToBoardModal';
import ConfirmModal from '../components/common/ConfirmModal';
import usePagination from '../hooks/usePagination';

const StandbyQueuePage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { items, loading, error } = useSelector((state) => state.standbyQueue);
  const { boards } = useSelector((state) => state.boards);

  const [assignModalShow, setAssignModalShow] = useState(false);
  const [retryModalShow, setRetryModalShow] = useState(false);
  const [discardModalShow, setDiscardModalShow] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  const {
    currentPage,
    pageSize,
    handlePageChange,
    handlePageSizeChange,
    getPaginatedData,
    getPaginationMetadata
  } = usePagination(1, 10);

  useEffect(() => {
    dispatch(fetchQueueItems());
    dispatch(fetchBoards());
  }, [dispatch]);

  const breadcrumbs = [
    { label: t('nav.dashboard') || 'Dashboard', path: '/dashboard' },
    { label: t('nav.standbyQueue') || 'Standby Queue' }
  ];

  const handleViewItem = (itemId) => {
    navigate(`/standby-queue/${itemId}`);
  };

  const openAssignModal = (item) => {
    setSelectedItem(item);
    setAssignModalShow(true);
  };

  const openRetryModal = (item) => {
    setSelectedItem(item);
    setRetryModalShow(true);
  };

  const openDiscardModal = (item) => {
    setSelectedItem(item);
    setDiscardModalShow(true);
  };

  const handleAssignToBoard = async (boardId) => {
    if (!selectedItem) return;

    setActionLoading(true);
    try {
      await dispatch(assignToBoard({ itemId: selectedItem.id, boardId })).unwrap();
      setAssignModalShow(false);
      setSelectedItem(null);
    } catch (err) {
      console.error('Failed to assign to board:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleRetryExternal = async () => {
    if (!selectedItem) return;

    setActionLoading(true);
    try {
      await dispatch(retryExternal(selectedItem.id)).unwrap();
      setRetryModalShow(false);
      setSelectedItem(null);
    } catch (err) {
      console.error('Failed to retry external sync:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDiscardItem = async () => {
    if (!selectedItem) return;

    setActionLoading(true);
    try {
      await dispatch(discardItem(selectedItem.id)).unwrap();
      setDiscardModalShow(false);
      setSelectedItem(null);
    } catch (err) {
      console.error('Failed to discard item:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const paginatedItems = getPaginatedData(items);
  const paginationMetadata = getPaginationMetadata(items.length);

  if (loading && items.length === 0) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Spinner fullPage message={t('common.loading')} />
      </ManagerLayout>
    );
  }

  return (
    <ManagerLayout breadcrumbs={breadcrumbs}>
      <div className="mb-4">
        <h1>{t('standbyQueue.title') || 'Standby Queue'}</h1>
        <p className="text-muted">
          {t('standbyQueue.description') || 'Review and assign tickets that could not be automatically routed'}
        </p>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error.message || t('standbyQueue.errors.loadFailed')}
        </Alert>
      )}

      <Row>
        <Col>
          {items.length === 0 ? (
            <Card>
              <EmptyState
                icon="bi-inbox-fill"
                title={t('standbyQueue.empty') || 'Queue is empty'}
                message={t('standbyQueue.emptyMessage') || 'All incoming tickets have been processed'}
              />
            </Card>
          ) : (
            <>
              <div className="mb-3">
                <small className="text-muted">
                  {t('standbyQueue.itemsCount', { count: items.length }) || `${items.length} items in queue`}
                </small>
              </div>

              {paginatedItems.map((item) => (
                <QueueItemCard
                  key={item.id}
                  item={item}
                  onView={() => handleViewItem(item.id)}
                  onAssign={() => openAssignModal(item)}
                  onRetry={() => openRetryModal(item)}
                  onDiscard={() => openDiscardModal(item)}
                />
              ))}

              {paginationMetadata.totalPages > 1 && (
                <Card>
                  <Pagination
                    currentPage={currentPage}
                    totalPages={paginationMetadata.totalPages}
                    pageSize={pageSize}
                    onPageChange={handlePageChange}
                    onPageSizeChange={handlePageSizeChange}
                  />
                </Card>
              )}
            </>
          )}
        </Col>
      </Row>

      {/* Assign to Board Modal */}
      <AssignToBoardModal
        show={assignModalShow}
        onHide={() => {
          setAssignModalShow(false);
          setSelectedItem(null);
        }}
        boards={boards}
        onConfirm={handleAssignToBoard}
        loading={actionLoading}
      />

      {/* Retry External Modal */}
      <ConfirmModal
        show={retryModalShow}
        onHide={() => {
          setRetryModalShow(false);
          setSelectedItem(null);
        }}
        title={t('standbyQueue.retryExternal') || 'Retry External Sync'}
        message={t('standbyQueue.retryExternalConfirm') || 'Retry syncing this ticket to the external platform?'}
        confirmLabel={t('standbyQueue.retry') || 'Retry'}
        variant="primary"
        onConfirm={handleRetryExternal}
        loading={actionLoading}
      />

      {/* Discard Confirmation Modal */}
      <ConfirmModal
        show={discardModalShow}
        onHide={() => {
          setDiscardModalShow(false);
          setSelectedItem(null);
        }}
        title={t('standbyQueue.discardItem') || 'Discard Item'}
        message={t('standbyQueue.discardConfirm') || 'Are you sure you want to discard this item? This action cannot be undone.'}
        confirmLabel={t('standbyQueue.discard') || 'Discard'}
        variant="danger"
        onConfirm={handleDiscardItem}
        loading={actionLoading}
      />
    </ManagerLayout>
  );
};

export default StandbyQueuePage;
