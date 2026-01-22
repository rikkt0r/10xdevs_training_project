import React, { useState, useEffect } from 'react';
import { Form } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import { useSelector, useDispatch } from 'react-redux';
import { fetchBoards } from '../../store/slices/boardsSlice';
import FormGroup from '../common/FormGroup';
import Input from '../common/Input';
import Select from '../common/Select';
import Button from '../common/Button';
import Alert from '../common/Alert';
import useFormValidation from '../../hooks/useFormValidation';
import { validateRequired, validateEmail, validatePort } from '../../utils/validationUtils';
import inboxService from '../../services/inboxService';

/**
 * InboxForm component
 * Form for creating or editing an email inbox
 */
const InboxForm = ({ initialValues = {}, onSubmit }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { boards } = useSelector((state) => state.boards);

  const [loading, setLoading] = useState(false);
  const [testLoading, setTestLoading] = useState(false);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    dispatch(fetchBoards());
  }, [dispatch]);

  const validationRules = {
    imap_host: (value) => validateRequired(value, t('settings.errors.imapHostRequired')),
    imap_port: (value) => {
      const requiredError = validateRequired(value, t('settings.errors.imapPortRequired'));
      if (requiredError) return requiredError;
      return validatePort(value, t('settings.errors.invalidPort'));
    },
    imap_username: (value) => {
      const requiredError = validateRequired(value, t('settings.errors.imapUsernameRequired'));
      if (requiredError) return requiredError;
      return validateEmail(value, t('settings.errors.invalidEmail'));
    },
    imap_password: (value) => validateRequired(value, t('settings.errors.imapPasswordRequired')),
    polling_interval: (value) => validateRequired(value, t('settings.errors.pollingIntervalRequired')),
  };

  const {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit,
  } = useFormValidation(
    {
      imap_host: initialValues.imap_host || '',
      imap_port: initialValues.imap_port || 993,
      imap_username: initialValues.imap_username || '',
      imap_password: initialValues.imap_password || '',
      use_ssl: initialValues.use_ssl !== undefined ? initialValues.use_ssl : true,
      polling_interval: initialValues.polling_interval || 300,
      board_id: initialValues.board_id || '',
    },
    validationRules
  );

  const boardOptions = [
    { value: '', label: t('settings.noBoardExclusive') || 'No exclusive board' },
    ...boards
      .filter(board => !board.archived)
      .map(board => ({
        value: board.id,
        label: board.name,
      }))
  ];

  const handleTestConnection = async () => {
    setTestLoading(true);
    setTestResult(null);

    try {
      await inboxService.testInboxConfig({
        imap_host: values.imap_host,
        imap_port: values.imap_port,
        imap_username: values.imap_username,
        imap_password: values.imap_password,
        use_ssl: values.use_ssl,
      });
      setTestResult({
        success: true,
        message: t('settings.connectionSuccess') || 'Connection test successful!'
      });
    } catch (err) {
      setTestResult({
        success: false,
        message: err.response?.data?.error?.message || t('settings.connectionFailed') || 'Connection test failed'
      });
    } finally {
      setTestLoading(false);
    }
  };

  const onFormSubmit = async (formValues) => {
    setLoading(true);
    try {
      await onSubmit({
        ...formValues,
        board_id: formValues.board_id || null,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      {testResult && (
        <Alert
          variant={testResult.success ? 'success' : 'danger'}
          dismissible
          onClose={() => setTestResult(null)}
          className="mb-4"
        >
          {testResult.message}
        </Alert>
      )}

      <h5 className="mb-3">{t('settings.imapSettings') || 'IMAP Settings'}</h5>

      <FormGroup
        label={t('settings.imapHost') || 'IMAP Server'}
        error={touched.imap_host && errors.imap_host}
        required
        htmlFor="imap_host"
        helpText={t('settings.imapHostHelp') || 'e.g., imap.gmail.com'}
      >
        <Input
          type="text"
          id="imap_host"
          name="imap_host"
          value={values.imap_host}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.imap_host && errors.imap_host}
          placeholder="imap.example.com"
        />
      </FormGroup>

      <FormGroup
        label={t('settings.imapPort') || 'IMAP Port'}
        error={touched.imap_port && errors.imap_port}
        required
        htmlFor="imap_port"
        helpText={t('settings.imapPortHelp') || 'Usually 993 for SSL'}
      >
        <Input
          type="number"
          id="imap_port"
          name="imap_port"
          value={values.imap_port}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.imap_port && errors.imap_port}
          placeholder="993"
        />
      </FormGroup>

      <FormGroup
        label={t('settings.imapUsername') || 'Email Address'}
        error={touched.imap_username && errors.imap_username}
        required
        htmlFor="imap_username"
      >
        <Input
          type="email"
          id="imap_username"
          name="imap_username"
          value={values.imap_username}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.imap_username && errors.imap_username}
          placeholder="support@example.com"
        />
      </FormGroup>

      <FormGroup
        label={t('settings.imapPassword') || 'Password'}
        error={touched.imap_password && errors.imap_password}
        required
        htmlFor="imap_password"
        helpText={t('settings.imapPasswordHelp') || 'For Gmail, use an app-specific password'}
      >
        <Input
          type="password"
          id="imap_password"
          name="imap_password"
          value={values.imap_password}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.imap_password && errors.imap_password}
          placeholder={t('settings.password') || 'Password'}
        />
      </FormGroup>

      <hr className="my-4" />

      <h5 className="mb-3">{t('settings.inboxSettings') || 'Inbox Settings'}</h5>

      <FormGroup
        label={t('settings.pollingInterval') || 'Polling Interval (seconds)'}
        error={touched.polling_interval && errors.polling_interval}
        required
        htmlFor="polling_interval"
        helpText={t('settings.pollingIntervalHelp') || 'How often to check for new emails'}
      >
        <Input
          type="number"
          id="polling_interval"
          name="polling_interval"
          value={values.polling_interval}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.polling_interval && errors.polling_interval}
          placeholder="300"
        />
      </FormGroup>

      <FormGroup
        label={t('settings.exclusiveBoard') || 'Exclusive Board (Optional)'}
        htmlFor="board_id"
        helpText={t('settings.exclusiveBoardHelp') || 'All emails from this inbox will go to this board'}
      >
        <Select
          id="board_id"
          name="board_id"
          value={values.board_id}
          onChange={handleChange}
          onBlur={handleBlur}
          options={boardOptions}
        />
      </FormGroup>

      <div className="d-flex gap-2 justify-content-end mt-4">
        <Button
          variant="outline-secondary"
          onClick={handleTestConnection}
          loading={testLoading}
          type="button"
        >
          <i className="bi bi-plug me-2" />
          {t('settings.testConnection') || 'Test Connection'}
        </Button>
        <Button
          type="submit"
          variant="primary"
          loading={loading}
        >
          {initialValues.id ? t('common.save') : t('common.create')}
        </Button>
      </div>
    </Form>
  );
};

export default InboxForm;
