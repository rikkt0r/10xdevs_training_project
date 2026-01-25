import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Row, Col } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import inboxService from '../services/inboxService';
import ManagerLayout from '../components/layout/ManagerLayout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import EmptyState from '../components/common/EmptyState';
import Alert from '../components/common/Alert';
import ConfirmModal from '../components/common/ConfirmModal';
import InboxCard from '../components/settings/InboxCard';
import ConnectionTestModal from '../components/settings/ConnectionTestModal';

const InboxListPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [inboxes, setInboxes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteModalShow, setDeleteModalShow] = useState(false);
  const [selectedInbox, setSelectedInbox] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [testModalShow, setTestModalShow] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [testLoading, setTestLoading] = useState(false);

  const loadInboxes = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await inboxService.getInboxes();
      setInboxes(response.data.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || t('settings.errors.loadInboxesFailed'));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    loadInboxes();
  }, [loadInboxes]);

  const breadcrumbs = [
    { label: t('nav.dashboard') || 'Dashboard', path: '/dashboard' },
    { label: t('nav.settings') || 'Settings', path: '/settings' },
    { label: t('settings.inboxes') || 'Email Inboxes' }
  ];

  const handleCreateInbox = () => {
    navigate('/settings/inboxes/new');
  };

  const handleEditInbox = (inboxId) => {
    navigate(`/settings/inboxes/${inboxId}/edit`);
  };

  const handleTestConnection = async (inboxId) => {
    setTestModalShow(true);
    setTestLoading(true);
    setTestResult(null);

    try {
      const response = await inboxService.testConnection(inboxId);
      setTestResult(response.data);
    } catch (err) {
      setTestResult(
        err.response?.data || {
          data: {
            imap_status: 'failed',
            smtp_status: 'failed',
            imap_error: t('settings.connectionFailed') || 'Connection test failed',
            smtp_error: t('settings.connectionFailed') || 'Connection test failed',
          },
        }
      );
    } finally {
      setTestLoading(false);
    }
  };

  const openDeleteModal = (inbox) => {
    setSelectedInbox(inbox);
    setDeleteModalShow(true);
  };

  const handleDeleteInbox = async () => {
    if (!selectedInbox) return;

    setActionLoading(true);
    try {
      await inboxService.deleteInbox(selectedInbox.id);
      setDeleteModalShow(false);
      setSelectedInbox(null);
      await loadInboxes();
    } catch (err) {
      console.error('Failed to delete inbox:', err);
      alert(t('settings.errors.deleteInboxFailed') || 'Failed to delete inbox');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Spinner fullPage message={t('common.loading')} />
      </ManagerLayout>
    );
  }

  return (
    <ManagerLayout breadcrumbs={breadcrumbs}>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>{t('settings.inboxes') || 'Email Inboxes'}</h1>
          <p className="text-muted mb-0">
            {t('settings.inboxesDescription') || 'Configure email accounts for receiving tickets'}
          </p>
        </div>
        <Button variant="primary" onClick={handleCreateInbox}>
          <i className="bi bi-plus-circle me-2" />
          {t('settings.addInbox') || 'Add Inbox'}
        </Button>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
        </Alert>
      )}

      <Row>
        <Col>
          {inboxes.length === 0 ? (
            <Card>
              <EmptyState
                icon="bi-inbox"
                title={t('settings.noInboxes') || 'No inboxes configured'}
                message={t('settings.noInboxesMessage') || 'Add an email inbox to start receiving tickets'}
                actionLabel={t('settings.addInbox') || 'Add Inbox'}
                onAction={handleCreateInbox}
              />
            </Card>
          ) : (
            <Row>
              {inboxes.map((inbox) => (
                <Col key={inbox.id} lg={6} className="mb-4">
                  <InboxCard
                    inbox={inbox}
                    onEdit={() => handleEditInbox(inbox.id)}
                    onTest={() => handleTestConnection(inbox.id)}
                    onDelete={() => openDeleteModal(inbox)}
                    testing={testLoading}
                  />
                </Col>
              ))}
            </Row>
          )}
        </Col>
      </Row>

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        show={deleteModalShow}
        onHide={() => {
          setDeleteModalShow(false);
          setSelectedInbox(null);
        }}
        title={t('settings.deleteInbox') || 'Delete Inbox'}
        message={t('settings.deleteInboxConfirm', { email: selectedInbox?.imap_username }) || `Are you sure you want to delete the inbox "${selectedInbox?.imap_username}"?`}
        confirmLabel={t('common.delete') || 'Delete'}
        variant="danger"
        onConfirm={handleDeleteInbox}
        loading={actionLoading}
      />

      {/* Connection Test Modal */}
      <ConnectionTestModal
        show={testModalShow}
        onHide={() => {
          setTestModalShow(false);
          setTestResult(null);
        }}
        testResult={testResult}
        loading={testLoading}
      />
    </ManagerLayout>
  );
};

export default InboxListPage;
