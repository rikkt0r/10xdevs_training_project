import React, { useState } from 'react';
import { Modal, Form, ProgressBar } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import Button from '../common/Button';
import Input from '../common/Input';
import FormGroup from '../common/FormGroup';
import Alert from '../common/Alert';
import useFormValidation from '../../hooks/useFormValidation';
import { validateRequired } from '../../utils/validationUtils';

/**
 * SuspendAccountWizard component
 * Multi-step wizard for account suspension with message and password confirmation
 */
const SuspendAccountWizard = ({ show, onHide, onConfirm, loading = false }) => {
  const { t } = useTranslation();
  const [currentStep, setCurrentStep] = useState(1);
  const [suspensionMessage, setSuspensionMessage] = useState('');
  const [password, setPassword] = useState('');

  const totalSteps = 3;
  const progressPercentage = (currentStep / totalSteps) * 100;

  // Validation rules for step 1 (suspension message)
  const step1ValidationRules = {
    suspensionMessage: (value) =>
      validateRequired(value, t('settings.errors.suspensionMessageRequired')),
  };

  const {
    values: step1Values,
    errors: step1Errors,
    touched: step1Touched,
    handleChange: handleStep1Change,
    handleBlur: handleStep1Blur,
    handleSubmit: handleStep1Submit,
    setFieldValue: setStep1FieldValue,
  } = useFormValidation(
    {
      suspensionMessage: '',
    },
    step1ValidationRules
  );

  // Validation rules for step 2 (password)
  const step2ValidationRules = {
    password: (value) => validateRequired(value, t('settings.errors.passwordRequired')),
  };

  const {
    values: step2Values,
    errors: step2Errors,
    touched: step2Touched,
    handleChange: handleStep2Change,
    handleBlur: handleStep2Blur,
    handleSubmit: handleStep2Submit,
  } = useFormValidation(
    {
      password: '',
    },
    step2ValidationRules
  );

  const handleClose = () => {
    setCurrentStep(1);
    setSuspensionMessage('');
    setPassword('');
    setStep1FieldValue('suspensionMessage', '');
    onHide();
  };

  const handleStep1Continue = (formValues) => {
    setSuspensionMessage(formValues.suspensionMessage);
    setCurrentStep(2);
  };

  const handleStep2Continue = (formValues) => {
    setPassword(formValues.password);
    setCurrentStep(3);
  };

  const handleFinalConfirm = () => {
    onConfirm({
      suspensionMessage,
      password,
    });
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <Form onSubmit={handleStep1Submit(handleStep1Continue)}>
            <Alert variant="warning" className="mb-3">
              <strong>{t('settings.warning') || 'Warning'}:</strong>{' '}
              {t('settings.suspensionWarningMessage') ||
                'Suspending your account is irreversible. All your boards will be disabled, and users will not be able to submit new tickets.'}
            </Alert>

            <FormGroup
              label={t('settings.suspensionMessage') || 'Suspension Message'}
              error={step1Touched.suspensionMessage && step1Errors.suspensionMessage}
              required
              htmlFor="suspensionMessage"
              helpText={
                t('settings.suspensionMessageHelp') ||
                'This message will be displayed to users who try to access your boards'
              }
            >
              <Form.Control
                as="textarea"
                rows={4}
                id="suspensionMessage"
                name="suspensionMessage"
                value={step1Values.suspensionMessage}
                onChange={handleStep1Change}
                onBlur={handleStep1Blur}
                isInvalid={step1Touched.suspensionMessage && step1Errors.suspensionMessage}
                placeholder={
                  t('settings.suspensionMessagePlaceholder') ||
                  'This service is no longer available. Please contact us at...'
                }
              />
              {step1Touched.suspensionMessage && step1Errors.suspensionMessage && (
                <Form.Control.Feedback type="invalid">
                  {step1Errors.suspensionMessage}
                </Form.Control.Feedback>
              )}
            </FormGroup>

            <div className="d-flex justify-content-end gap-2 mt-4">
              <Button variant="outline-secondary" onClick={handleClose}>
                {t('common.cancel') || 'Cancel'}
              </Button>
              <Button type="submit" variant="danger">
                {t('common.continue') || 'Continue'}
              </Button>
            </div>
          </Form>
        );

      case 2:
        return (
          <Form onSubmit={handleStep2Submit(handleStep2Continue)}>
            <Alert variant="info" className="mb-3">
              {t('settings.confirmPasswordPrompt') ||
                'Please enter your password to confirm this action.'}
            </Alert>

            <div className="mb-3">
              <strong>{t('settings.suspensionMessage') || 'Suspension Message'}:</strong>
              <div className="p-2 mt-2 bg-light border rounded">
                <p className="mb-0 text-muted">{suspensionMessage}</p>
              </div>
            </div>

            <FormGroup
              label={t('settings.password') || 'Password'}
              error={step2Touched.password && step2Errors.password}
              required
              htmlFor="password"
            >
              <Input
                type="password"
                id="password"
                name="password"
                value={step2Values.password}
                onChange={handleStep2Change}
                onBlur={handleStep2Blur}
                error={step2Touched.password && step2Errors.password}
                placeholder={t('settings.enterPassword') || 'Enter your password'}
              />
            </FormGroup>

            <div className="d-flex justify-content-end gap-2 mt-4">
              <Button variant="outline-secondary" onClick={() => setCurrentStep(1)}>
                {t('common.back') || 'Back'}
              </Button>
              <Button type="submit" variant="danger">
                {t('common.continue') || 'Continue'}
              </Button>
            </div>
          </Form>
        );

      case 3:
        return (
          <>
            <Alert variant="danger" className="mb-3">
              <strong>{t('settings.finalWarning') || 'Final Warning'}:</strong>
              <p className="mb-0 mt-2">
                {t('settings.suspensionFinalConfirm') ||
                  'You are about to suspend your account. This action cannot be undone. Are you absolutely sure?'}
              </p>
            </Alert>

            <div className="mb-3">
              <strong>{t('settings.suspensionMessage') || 'Suspension Message'}:</strong>
              <div className="p-2 mt-2 bg-light border rounded">
                <p className="mb-0 text-muted">{suspensionMessage}</p>
              </div>
            </div>

            <div className="mb-4">
              <h6>{t('settings.whatHappensNext') || 'What happens next'}:</h6>
              <ul className="text-muted">
                <li>{t('settings.boardsDisabled') || 'All your boards will be disabled'}</li>
                <li>
                  {t('settings.noNewTickets') || 'No new tickets can be submitted via web forms'}
                </li>
                <li>
                  {t('settings.emailAutoReply') ||
                    'Incoming emails will receive an auto-reply with your suspension message'}
                </li>
                <li>
                  {t('settings.existingTicketsViewable') ||
                    'Existing tickets remain viewable via their secret links'}
                </li>
                <li>
                  {t('settings.cannotReactivate') ||
                    'You will need to contact support to reactivate your account'}
                </li>
              </ul>
            </div>

            <div className="d-flex justify-content-end gap-2 mt-4">
              <Button variant="outline-secondary" onClick={() => setCurrentStep(2)}>
                {t('common.back') || 'Back'}
              </Button>
              <Button variant="danger" onClick={handleFinalConfirm} loading={loading}>
                {t('settings.suspendAccount') || 'Suspend Account'}
              </Button>
            </div>
          </>
        );

      default:
        return null;
    }
  };

  return (
    <Modal show={show} onHide={handleClose} size="lg" backdrop="static" keyboard={!loading}>
      <Modal.Header closeButton={!loading}>
        <Modal.Title>
          {t('settings.suspendAccount') || 'Suspend Account'} - {t('common.step') || 'Step'}{' '}
          {currentStep} {t('common.of') || 'of'} {totalSteps}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <ProgressBar now={progressPercentage} className="mb-4" />
        {renderStepContent()}
      </Modal.Body>
    </Modal>
  );
};

export default SuspendAccountWizard;
