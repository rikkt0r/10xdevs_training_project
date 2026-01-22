import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { Form } from 'react-bootstrap';
import { fetchProfile, updateProfile } from '../store/slices/settingsSlice';
import ManagerLayout from '../components/layout/ManagerLayout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Select from '../components/common/Select';
import FormGroup from '../components/common/FormGroup';
import Alert from '../components/common/Alert';
import Spinner from '../components/common/Spinner';
import useFormValidation from '../hooks/useFormValidation';
import { validateRequired } from '../utils/validationUtils';
import { getTimezones, getBrowserTimezone } from '../utils/timezoneUtils';

const ProfileSettingsPage = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { profile, loading, error } = useSelector((state) => state.settings);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    dispatch(fetchProfile());
  }, [dispatch]);

  const validationRules = {
    name: (value) => validateRequired(value, t('settings.errors.nameRequired')),
  };

  const {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
  } = useFormValidation(
    {
      name: profile?.name || '',
      email: profile?.email || '',
      timezone: profile?.timezone || getBrowserTimezone(),
    },
    validationRules
  );

  useEffect(() => {
    if (profile) {
      setFieldValue('name', profile.name);
      setFieldValue('email', profile.email);
      setFieldValue('timezone', profile.timezone || getBrowserTimezone());
    }
  }, [profile, setFieldValue]);

  const breadcrumbs = [
    { label: t('nav.dashboard') || 'Dashboard', path: '/dashboard' },
    { label: t('nav.settings') || 'Settings', path: '/settings' },
    { label: t('settings.profile') || 'Profile' }
  ];

  const onSubmit = async (formValues) => {
    try {
      await dispatch(updateProfile({
        name: formValues.name,
        timezone: formValues.timezone,
      })).unwrap();
      setSuccessMessage(t('settings.profileUpdated') || 'Profile updated successfully');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Failed to update profile:', err);
    }
  };

  if (loading && !profile) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Spinner fullPage message={t('common.loading')} />
      </ManagerLayout>
    );
  }

  return (
    <ManagerLayout breadcrumbs={breadcrumbs}>
      <div className="mb-4">
        <h1>{t('settings.profile') || 'Profile Settings'}</h1>
        <p className="text-muted">
          {t('settings.profileDescription') || 'Manage your account information'}
        </p>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error.message || t('settings.errors.loadFailed')}
        </Alert>
      )}

      {successMessage && (
        <Alert variant="success" className="mb-4">
          {successMessage}
        </Alert>
      )}

      <Card className="col-lg-6">
        <Form onSubmit={handleSubmit(onSubmit)}>
          <FormGroup
            label={t('settings.name') || 'Name'}
            error={touched.name && errors.name}
            required
            htmlFor="name"
          >
            <Input
              type="text"
              id="name"
              name="name"
              value={values.name}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.name && errors.name}
              placeholder={t('settings.namePlaceholder') || 'Enter your name'}
            />
          </FormGroup>

          <FormGroup
            label={t('settings.email') || 'Email'}
            helpText={t('settings.emailReadOnly') || 'Email cannot be changed'}
            htmlFor="email"
          >
            <Input
              type="email"
              id="email"
              name="email"
              value={values.email}
              disabled
              readOnly
            />
          </FormGroup>

          <FormGroup
            label={t('settings.timezone') || 'Timezone'}
            helpText={t('settings.timezoneHelp') || 'Select your preferred timezone for displaying dates'}
            htmlFor="timezone"
          >
            <Select
              id="timezone"
              name="timezone"
              value={values.timezone}
              onChange={handleChange}
              onBlur={handleBlur}
              options={getTimezones()}
            />
          </FormGroup>

          <div className="d-flex justify-content-end mt-4">
            <Button
              type="submit"
              variant="primary"
              loading={loading}
            >
              {t('common.save') || 'Save Changes'}
            </Button>
          </div>
        </Form>
      </Card>
    </ManagerLayout>
  );
};

export default ProfileSettingsPage;
