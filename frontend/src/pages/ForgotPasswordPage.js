import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { Form, Button, Card, Alert, Container, Row, Col } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import { forgotPassword, clearError } from '../store/slices/authSlice';

const ForgotPasswordPage = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.auth);

  const [email, setEmail] = useState('');
  const [emailSent, setEmailSent] = useState(false);
  const [validationError, setValidationError] = useState('');

  useEffect(() => {
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email) {
      setValidationError(t('auth.errors.emailRequired'));
      return;
    }

    if (!/\S+@\S+\.\S+/.test(email)) {
      setValidationError(t('auth.errors.emailInvalid'));
      return;
    }

    const result = await dispatch(forgotPassword(email));

    if (result.type === 'auth/forgotPassword/fulfilled') {
      setEmailSent(true);
    }
  };

  if (emailSent) {
    return (
      <Container>
        <Row className="justify-content-center mt-5">
          <Col md={6} lg={5}>
            <Card>
              <Card.Body>
                <h2 className="text-center mb-4">{t('auth.resetEmailSent')}</h2>
                <Alert variant="success">
                  <p>{t('auth.resetEmailSentMessage')}</p>
                  <p>{t('auth.checkYourEmail')}</p>
                </Alert>
                <div className="text-center">
                  <Link to="/login" className="btn btn-primary">
                    {t('auth.backToLogin')}
                  </Link>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  return (
    <Container>
      <Row className="justify-content-center mt-5">
        <Col md={6} lg={5}>
          <Card>
            <Card.Body>
              <h2 className="text-center mb-4">{t('auth.forgotPassword')}</h2>

              <p className="text-muted text-center mb-4">
                {t('auth.forgotPasswordInstructions')}
              </p>

              {error && (
                <Alert variant="danger" dismissible onClose={() => dispatch(clearError())}>
                  {error.message || t('auth.errors.forgotPasswordFailed')}
                </Alert>
              )}

              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3" controlId="email">
                  <Form.Label>{t('auth.email')}</Form.Label>
                  <Form.Control
                    type="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      if (validationError) setValidationError('');
                    }}
                    isInvalid={!!validationError}
                    placeholder={t('auth.emailPlaceholder')}
                  />
                  <Form.Control.Feedback type="invalid">
                    {validationError}
                  </Form.Control.Feedback>
                </Form.Group>

                <Button variant="primary" type="submit" disabled={loading} className="w-100">
                  {loading ? t('common.loading') : t('auth.sendResetLink')}
                </Button>
              </Form>

              <div className="text-center mt-3">
                <Link to="/login">{t('auth.backToLogin')}</Link>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ForgotPasswordPage;
