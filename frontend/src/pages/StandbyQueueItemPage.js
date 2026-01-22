import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Row, Col } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { fetchQueueItem, assignToBoard, retryExternal, discardItem } from '../store/slices/standbyQueueSlice';
import { fetchBoards } from '../store/slices/boardsSlice';
import ManagerLayout from '../components/layout/ManagerLayout';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import Alert from '../components/common/Alert';
import { formatDateTime, formatRelativeDate } from '../utils/dateUtils';
import AssignToBoardModal from '../components/standbyQueue/AssignToBoardModal';
import ConfirmModal from '../components/common/ConfirmModal';

const StandbyQueueItemPage = () => {
  const { t, i18n } = useTranslation();
  const { itemId } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { currentItem, loading, error } = useSelector((state) => state.standbyQueue);
  const { boards } = useSelector((state) => state.boards);

  const [assignModalShow, setAssignModalShow] = useState(false);
  const [retryModalShow, setRetryModalShow] = useState(false);
  const [discardModalShow, setDiscardModalShow] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (itemId) {
      dispatch(fetchQueueItem(itemId));
      dispatch(fetchBoards());
    }
  }, [dispatch, itemId]);

  const breadcrumbs = [
    { label: t('nav.dashboard') || 'Dashboard', path: '/dashboard' },
    { label: t('nav.standbyQueue') || 'Standby Queue', path: '/standby-queue' },
    { label: `#${itemId}` }
  ];

  const handleAssignToBoard = async (boardId) => {
    setActionLoading(true);
    try {
      await dispatch(assignToBoard({ itemId, boardId })).unwrap();
      navigate('/standby-queue');
    } catch (err) {
      console.error('Failed to assign to board:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleRetryExternal = async () => {
    setActionLoading(true);
    try {
      await dispatch(retryExternal(itemId)).unwrap();
      setRetryModalShow(false);
    } catch (err) {
      console.error('Failed to retry external sync:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDiscardItem = async () => {
    setActionLoading(true);
    try {
      await dispatch(discardItem(itemId)).unwrap();
      navigate('/standby-queue');
    } catch (err) {
      console.error('Failed to discard item:', err);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading && !currentItem) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Spinner fullPage message={t('common.loading')} />
      </ManagerLayout>
    );
  }

  if (error) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Alert variant="danger">{error.message || t('standbyQueue.errors.loadFailed')}</Alert>
      </ManagerLayout>
    );
  }

  if (!currentItem) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Alert variant="warning">{t('standbyQueue.notFound') || 'Queue item not found'}</Alert>
      </ManagerLayout>
    );
  }

  return (
    <ManagerLayout breadcrumbs={breadcrumbs}>
      <Row>
        <Col lg={8}>
          {/* Email Preview */}
          <Card className="mb-4">
            <div className="d-flex justify-content-between align-items-start mb-3">
              <div>
                <h3 className="mb-2">{currentItem.subject}</h3>
                <div className="text-muted">
                  <small>
                    <i className="bi bi-person me-1" />
                    {currentItem.sender_email}
                  </small>
                  <span className="mx-2">•</span>
                  <small>
                    <i className="bi bi-clock me-1" />
                    {formatRelativeDate(currentItem.received_at, i18n.language)}
                  </small>
                </div>
              </div>
            </div>

            <hr />

            {/* Email Body */}
            <div>
              <strong className="mb-2 d-block">{t('standbyQueue.emailBody') || 'Email Body'}:</strong>
              <div className="p-3 bg-light rounded">
                <pre className="mb-0" style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                  {currentItem.body}
                </pre>
              </div>
            </div>
          </Card>
        </Col>

        <Col lg={4}>
          {/* Queue Info */}
          <Card title={t('standbyQueue.queueInfo') || 'Queue Information'} className="mb-4">
            <div className="mb-3">
              <strong>{t('standbyQueue.reason') || 'Reason'}:</strong>
              <div>
                <Badge variant="warning" className="mt-1">
                  {currentItem.reason || t('standbyQueue.noKeywordMatch') || 'No keyword match'}
                </Badge>
              </div>
            </div>

            <div className="mb-3">
              <strong>{t('standbyQueue.receivedAt') || 'Received At'}:</strong>
              <div className="text-muted">{formatDateTime(currentItem.received_at, i18n.language)}</div>
            </div>

            {currentItem.external_sync_failed && (
              <div className="mb-3">
                <Badge variant="danger">
                  <i className="bi bi-exclamation-triangle me-1" />
                  {t('standbyQueue.externalSyncFailed') || 'External sync failed'}
                </Badge>
              </div>
            )}
          </Card>

          {/* Actions */}
          <Card title={t('standbyQueue.actions') || 'Actions'}>
            <div className="d-grid gap-2">
              <Button
                variant="primary"
                onClick={() => setAssignModalShow(true)}
              >
                <i className="bi bi-kanban me-2" />
                {t('standbyQueue.assignToBoard') || 'Assign to Board'}
              </Button>

              {currentItem.external_sync_failed && (
                <Button
                  variant="warning"
                  onClick={() => setRetryModalShow(true)}
                >
                  <i className="bi bi-arrow-repeat me-2" />
                  {t('standbyQueue.retryExternal') || 'Retry External Sync'}
                </Button>
              )}

              <Button
                variant="danger"
                onClick={() => setDiscardModalShow(true)}
              >
                <i className="bi bi-trash me-2" />
                {t('standbyQueue.discard') || 'Discard'}
              </Button>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Assign to Board Modal */}
      <AssignToBoardModal
        show={assignModalShow}
        onHide={() => setAssignModalShow(false)}
        boards={boards}
        onConfirm={handleAssignToBoard}
        loading={actionLoading}
      />

      {/* Retry External Modal */}
      <ConfirmModal
        show={retryModalShow}
        onHide={() => setRetryModalShow(false)}
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
        onHide={() => setDiscardModalShow(false)}
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

export default StandbyQueueItemPage;
