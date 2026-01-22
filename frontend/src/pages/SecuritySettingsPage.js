import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Row, Col } from 'react-bootstrap';
import { changePassword, suspendAccount } from '../store/slices/settingsSlice';
import { logout } from '../store/slices/authSlice';
import ManagerLayout from '../components/layout/ManagerLayout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import FormGroup from '../components/common/FormGroup';
import Alert from '../components/common/Alert';
import SuspendAccountWizard from '../components/settings/SuspendAccountWizard';
import useFormValidation from '../hooks/useFormValidation';
import { validateRequired, validatePassword, validatePasswordConfirmation } from '../utils/validationUtils';

const SecuritySettingsPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.settings);

  const [successMessage, setSuccessMessage] = useState('');
  const [suspendModalShow, setSuspendModalShow] = useState(false);
  const [suspending, setSuspending] = useState(false);

  const validationRules = {
    currentPassword: (value) => validateRequired(value, t('settings.errors.currentPasswordRequired')),
    newPassword: (value) => {
      const requiredError = validateRequired(value, t('settings.errors.newPasswordRequired'));
      if (requiredError) return requiredError;
      return validatePassword(value, t('settings.errors.passwordWeak'));
    },
    confirmPassword: (value, allValues) => {
      const requiredError = validateRequired(value, t('settings.errors.confirmPasswordRequired'));
      if (requiredError) return requiredError;
      return validatePasswordConfirmation(allValues.newPassword, value, t('settings.errors.passwordsDoNotMatch'));
    },
  };

  const {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
  } = useFormValidation(
    {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    },
    validationRules
  );

  const breadcrumbs = [
    { label: t('nav.dashboard') || 'Dashboard', path: '/dashboard' },
    { label: t('nav.settings') || 'Settings', path: '/settings' },
    { label: t('settings.security') || 'Security' }
  ];

  const onSubmit = async (formValues) => {
    try {
      await dispatch(changePassword({
        currentPassword: formValues.currentPassword,
        newPassword: formValues.newPassword,
      })).unwrap();

      setSuccessMessage(t('settings.passwordChanged') || 'Password changed successfully');
      resetForm();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Failed to change password:', err);
    }
  };

  const handleSuspendAccount = async ({ suspensionMessage, password }) => {
    setSuspending(true);
    try {
      await dispatch(suspendAccount({ suspensionMessage, password })).unwrap();
      setSuspendModalShow(false);
      dispatch(logout());
      navigate('/login');
    } catch (err) {
      console.error('Failed to suspend account:', err);
    } finally {
      setSuspending(false);
    }
  };

  return (
    <ManagerLayout breadcrumbs={breadcrumbs}>
      <div className="mb-4">
        <h1>{t('settings.security') || 'Security Settings'}</h1>
        <p className="text-muted">
          {t('settings.securityDescription') || 'Manage your password and account security'}
        </p>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error.message || t('settings.errors.saveFailed')}
        </Alert>
      )}

      {successMessage && (
        <Alert variant="success" className="mb-4">
          {successMessage}
        </Alert>
      )}

      <Row>
        <Col lg={6}>
          {/* Change Password */}
          <Card title={t('settings.changePassword') || 'Change Password'} className="mb-4">
            <Form onSubmit={handleSubmit(onSubmit)}>
              <FormGroup
                label={t('settings.currentPassword') || 'Current Password'}
                error={touched.currentPassword && errors.currentPassword}
                required
                htmlFor="currentPassword"
              >
                <Input
                  type="password"
                  id="currentPassword"
                  name="currentPassword"
                  value={values.currentPassword}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched.currentPassword && errors.currentPassword}
                  placeholder={t('settings.currentPasswordPlaceholder') || 'Enter current password'}
                />
              </FormGroup>

              <FormGroup
                label={t('settings.newPassword') || 'New Password'}
                error={touched.newPassword && errors.newPassword}
                helpText={t('settings.passwordRequirements') || 'At least 8 characters'}
                required
                htmlFor="newPassword"
              >
                <Input
                  type="password"
                  id="newPassword"
                  name="newPassword"
                  value={values.newPassword}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched.newPassword && errors.newPassword}
                  placeholder={t('settings.newPasswordPlaceholder') || 'Enter new password'}
                />
              </FormGroup>

              <FormGroup
                label={t('settings.confirmPassword') || 'Confirm New Password'}
                error={touched.confirmPassword && errors.confirmPassword}
                required
                htmlFor="confirmPassword"
              >
                <Input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={values.confirmPassword}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched.confirmPassword && errors.confirmPassword}
                  placeholder={t('settings.confirmPasswordPlaceholder') || 'Confirm new password'}
                />
              </FormGroup>

              <div className="d-flex justify-content-end mt-4">
                <Button
                  type="submit"
                  variant="primary"
                  loading={loading}
                >
                  {t('settings.changePassword') || 'Change Password'}
                </Button>
              </div>
            </Form>
          </Card>

          {/* Account Suspension */}
          <Card title={t('settings.dangerZone') || 'Danger Zone'}>
            <div className="alert alert-warning mb-3">
              <strong>{t('settings.suspendWarning') || 'Warning:'}:</strong>{' '}
              {t('settings.suspendDescription') || 'Suspending your account will log you out and prevent access until reactivated.'}
            </div>

            <Button
              variant="danger"
              onClick={() => setSuspendModalShow(true)}
            >
              {t('settings.suspendAccount') || 'Suspend Account'}
            </Button>
          </Card>
        </Col>
      </Row>

      {/* Suspend Account Wizard */}
      <SuspendAccountWizard
        show={suspendModalShow}
        onHide={() => setSuspendModalShow(false)}
        onConfirm={handleSuspendAccount}
        loading={suspending}
      />
    </ManagerLayout>
  );
};

export default SecuritySettingsPage;
