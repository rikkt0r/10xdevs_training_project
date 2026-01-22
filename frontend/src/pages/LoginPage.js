import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Form } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import { login, clearError } from '../store/slices/authSlice';
import PublicLayout from '../components/layout/PublicLayout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import FormGroup from '../components/common/FormGroup';
import Alert from '../components/common/Alert';

const LoginPage = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { loading, error, isAuthenticated } = useSelector((state) => state.auth);

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [validationErrors, setValidationErrors] = useState({});

  const from = location.state?.from?.pathname || '/dashboard';

  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

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

    if (!formData.email) {
      errors.email = t('auth.errors.emailRequired');
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = t('auth.errors.emailInvalid');
    }

    if (!formData.password) {
      errors.password = t('auth.errors.passwordRequired');
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    dispatch(login(formData));
  };

  return (
    <PublicLayout centered maxWidth="sm">
      <Card title={t('auth.login')} className="shadow-sm">
        {error && (
          <Alert
            variant="danger"
            dismissible
            onClose={() => dispatch(clearError())}
            className="mb-3"
          >
            {error.message || t('auth.errors.loginFailed')}
          </Alert>
        )}

        <Form onSubmit={handleSubmit}>
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

          <div className="d-flex justify-content-between align-items-center mb-3">
            <Link to="/forgot-password">{t('auth.forgotPassword')}</Link>
          </div>

          <Button
            variant="primary"
            type="submit"
            loading={loading}
            fullWidth
          >
            {t('auth.login')}
          </Button>
        </Form>

        <div className="text-center mt-3">
          <span>{t('auth.noAccount')} </span>
          <Link to="/register">{t('auth.register')}</Link>
        </div>
      </Card>
    </PublicLayout>
  );
};

export default LoginPage;
