import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import { Form } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import { register, clearError } from '../store/slices/authSlice';
import PublicLayout from '../components/layout/PublicLayout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import FormGroup from '../components/common/FormGroup';
import Alert from '../components/common/Alert';

const RegisterPage = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error, isAuthenticated } = useSelector((state) => state.auth);

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
  });

  const [validationErrors, setValidationErrors] = useState({});
  const [registrationSuccess, setRegistrationSuccess] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (validationErrors[name]) {
      setValidationErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.name) {
      errors.name = t('auth.errors.nameRequired');
    } else if (formData.name.length > 255) {
      errors.name = t('auth.errors.nameTooLong');
    }

    if (!formData.email) {
      errors.email = t('auth.errors.emailRequired');
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = t('auth.errors.emailInvalid');
    }

    if (!formData.password) {
      errors.password = t('auth.errors.passwordRequired');
    } else if (formData.password.length < 8) {
      errors.password = t('auth.errors.passwordTooShort');
    }

    if (!formData.confirmPassword) {
      errors.confirmPassword = t('auth.errors.confirmPasswordRequired');
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = t('auth.errors.passwordsDoNotMatch');
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const result = await dispatch(register({
      email: formData.email,
      password: formData.password,
      name: formData.name,
    }));

    if (result.type === 'auth/register/fulfilled') {
      setRegistrationSuccess(true);
    }
  };

  if (registrationSuccess) {
    return (
      <PublicLayout centered maxWidth="sm">
        <Card title={t('auth.registrationSuccess')} className="shadow-sm">
          <Alert variant="success" show>
            <p>{t('auth.verificationEmailSent')}</p>
            <p className="mb-0">{t('auth.checkYourEmail')}</p>
          </Alert>
          <div className="text-center mt-3">
            <Button variant="primary" onClick={() => navigate('/login')}>
              {t('auth.goToLogin')}
            </Button>
          </div>
        </Card>
      </PublicLayout>
    );
  }

  return (
    <PublicLayout centered maxWidth="sm">
      <Card title={t('auth.register')} className="shadow-sm">
        {error && (
          <Alert
            variant="danger"
            dismissible
            onClose={() => dispatch(clearError())}
            className="mb-3"
          >
            {error.message || t('auth.errors.registrationFailed')}
          </Alert>
        )}

        <Form onSubmit={handleSubmit}>
          <FormGroup
            label={t('auth.name')}
            error={validationErrors.name}
            htmlFor="name"
          >
            <Input
              type="text"
              name="name"
              id="name"
              value={formData.name}
              onChange={handleChange}
              error={validationErrors.name}
              placeholder={t('auth.namePlaceholder')}
            />
          </FormGroup>

          <FormGroup
            label={t('auth.email')}
            error={validationErrors.email}
            htmlFor="email"
          >
            <Input
              type="email"
              name="email"
              id="email"
              value={formData.email}
              onChange={handleChange}
              error={validationErrors.email}
              placeholder={t('auth.emailPlaceholder')}
            />
          </FormGroup>

          <FormGroup
            label={t('auth.password')}
            error={validationErrors.password}
            helpText={t('auth.passwordRequirements')}
            htmlFor="password"
          >
            <Input
              type="password"
              name="password"
              id="password"
              value={formData.password}
              onChange={handleChange}
              error={validationErrors.password}
              placeholder={t('auth.passwordPlaceholder')}
            />
          </FormGroup>

          <FormGroup
            label={t('auth.confirmPassword')}
            error={validationErrors.confirmPassword}
            htmlFor="confirmPassword"
          >
            <Input
              type="password"
              name="confirmPassword"
              id="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              error={validationErrors.confirmPassword}
              placeholder={t('auth.confirmPasswordPlaceholder')}
            />
          </FormGroup>

          <Button
            variant="primary"
            type="submit"
            loading={loading}
            fullWidth
          >
            {t('auth.register')}
          </Button>
        </Form>

        <div className="text-center mt-3">
          <span>{t('auth.haveAccount')} </span>
          <Link to="/login">{t('auth.login')}</Link>
        </div>
      </Card>
    </PublicLayout>
  );
};

export default RegisterPage;
