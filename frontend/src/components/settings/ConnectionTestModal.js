import React from 'react';
import { Modal } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import Button from '../common/Button';
import Alert from '../common/Alert';
import Spinner from '../common/Spinner';

/**
 * ConnectionTestModal component
 * Modal for displaying connection test results for email inboxes
 */
const ConnectionTestModal = ({ show, onHide, testResult, loading }) => {
  const { t } = useTranslation();

  const renderTestResult = () => {
    if (loading) {
      return (
        <div className="text-center py-4">
          <Spinner message={t('settings.testingConnection') || 'Testing connection...'} />
        </div>
      );
    }

    if (!testResult) {
      return null;
    }

    const { data } = testResult;

    // Check overall status
    const allSuccess = data.imap_status === 'success' && data.smtp_status === 'success';
    const hasFailure = data.imap_status === 'failed' || data.smtp_status === 'failed';

    return (
      <>
        {allSuccess && (
          <Alert variant="success" className="mb-3">
            <i className="bi bi-check-circle-fill me-2" />
            <strong>{t('settings.connectionTestSuccess') || 'Connection Test Successful'}</strong>
            <p className="mb-0 mt-2">
              {t('settings.connectionTestSuccessMessage') ||
                'Both IMAP and SMTP connections were established successfully.'}
            </p>
          </Alert>
        )}

        {hasFailure && (
          <Alert variant="danger" className="mb-3">
            <i className="bi bi-exclamation-triangle-fill me-2" />
            <strong>{t('settings.connectionTestFailed') || 'Connection Test Failed'}</strong>
            <p className="mb-0 mt-2">
              {t('settings.connectionTestFailedMessage') ||
                'One or more connections failed. Please check the details below.'}
            </p>
          </Alert>
        )}

        <div className="mb-3">
          <h6 className="mb-2">
            <i className="bi bi-download me-2" />
            {t('settings.imapConnection') || 'IMAP Connection'}
          </h6>
          <div className="p-3 border rounded bg-light">
            {data.imap_status === 'success' ? (
              <div className="text-success">
                <i className="bi bi-check-circle-fill me-2" />
                <strong>{t('settings.success') || 'Success'}</strong>
              </div>
            ) : (
              <div className="text-danger">
                <i className="bi bi-x-circle-fill me-2" />
                <strong>{t('settings.failed') || 'Failed'}</strong>
                {data.imap_error && (
                  <div className="mt-2 small text-muted">{data.imap_error}</div>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="mb-3">
          <h6 className="mb-2">
            <i className="bi bi-upload me-2" />
            {t('settings.smtpConnection') || 'SMTP Connection'}
          </h6>
          <div className="p-3 border rounded bg-light">
            {data.smtp_status === 'success' ? (
              <div className="text-success">
                <i className="bi bi-check-circle-fill me-2" />
                <strong>{t('settings.success') || 'Success'}</strong>
              </div>
            ) : (
              <div className="text-danger">
                <i className="bi bi-x-circle-fill me-2" />
                <strong>{t('settings.failed') || 'Failed'}</strong>
                {data.smtp_error && (
                  <div className="mt-2 small text-muted">{data.smtp_error}</div>
                )}
              </div>
            )}
          </div>
        </div>
      </>
    );
  };

  return (
    <Modal show={show} onHide={onHide} size="lg" centered>
      <Modal.Header closeButton>
        <Modal.Title>
          <i className="bi bi-plug me-2" />
          {t('settings.connectionTestResults') || 'Connection Test Results'}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>{renderTestResult()}</Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide} disabled={loading}>
          {t('common.close') || 'Close'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ConnectionTestModal;
