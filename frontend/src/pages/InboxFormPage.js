import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import inboxService from '../services/inboxService';
import ManagerLayout from '../components/layout/ManagerLayout';
import Card from '../components/common/Card';
import Spinner from '../components/common/Spinner';
import Alert from '../components/common/Alert';
import InboxForm from '../components/settings/InboxForm';

const InboxFormPage = () => {
  const { t } = useTranslation();
  const { inboxId } = useParams();
  const navigate = useNavigate();

  const [inbox, setInbox] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const isEditMode = !!inboxId;

  useEffect(() => {
    if (isEditMode) {
      loadInbox();
    }
  }, [inboxId, isEditMode]);

  const loadInbox = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await inboxService.getInbox(inboxId);
      setInbox(response.data.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || t('settings.errors.loadInboxFailed'));
    } finally {
      setLoading(false);
    }
  };

  const breadcrumbs = [
    { label: t('nav.dashboard') || 'Dashboard', path: '/dashboard' },
    { label: t('nav.settings') || 'Settings', path: '/settings' },
    { label: t('settings.inboxes') || 'Email Inboxes', path: '/settings/inboxes' },
    { label: isEditMode ? t('settings.editInbox') || 'Edit Inbox' : t('settings.addInbox') || 'Add Inbox' }
  ];

  const handleSubmit = async (values) => {
    try {
      if (isEditMode) {
        await inboxService.updateInbox(inboxId, values);
      } else {
        await inboxService.createInbox(values);
      }
      navigate('/settings/inboxes');
    } catch (err) {
      throw err;
    }
  };

  if (isEditMode && loading && !inbox) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Spinner fullPage message={t('common.loading')} />
      </ManagerLayout>
    );
  }

  return (
    <ManagerLayout breadcrumbs={breadcrumbs}>
      <div className="mb-4">
        <h1>
          {isEditMode ? t('settings.editInbox') || 'Edit Inbox' : t('settings.addInbox') || 'Add Inbox'}
        </h1>
        <p className="text-muted">
          {t('settings.inboxFormDescription') || 'Configure IMAP settings to receive emails'}
        </p>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
        </Alert>
      )}

      <Card className="col-lg-8">
        <InboxForm
          initialValues={isEditMode ? inbox : {}}
          onSubmit={handleSubmit}
        />
      </Card>
    </ManagerLayout>
  );
};

export default InboxFormPage;
