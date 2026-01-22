import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useSearchParams, Link } from 'react-router-dom';
import { Card, Alert, Container, Row, Col, Spinner, Button } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import { verifyEmail, resendVerification, clearError } from '../store/slices/authSlice';

const VerifyEmailPage = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [searchParams] = useSearchParams();
  const { loading, error } = useSelector((state) => state.auth);

  const [verificationStatus, setVerificationStatus] = useState('verifying');
  const [resendEmail, setResendEmail] = useState('');
  const [resendSuccess, setResendSuccess] = useState(false);

  const token = searchParams.get('token');

  useEffect(() => {
    if (token) {
      dispatch(verifyEmail(token)).then((result) => {
        if (result.type === 'auth/verifyEmail/fulfilled') {
          setVerificationStatus('success');
        } else {
          setVerificationStatus('failed');
        }
      });
    } else {
      setVerificationStatus('no-token');
    }
  }, [token, dispatch]);

  const handleResend = async (e) => {
    e.preventDefault();
    const result = await dispatch(resendVerification(resendEmail));
    if (result.type === 'auth/resendVerification/fulfilled') {
      setResendSuccess(true);
    }
  };

  if (verificationStatus === 'verifying') {
    return (
      <Container>
        <Row className="justify-content-center mt-5">
          <Col md={6} lg={5}>
            <Card>
              <Card.Body className="text-center">
                <Spinner animation="border" role="status" className="mb-3">
                  <span className="visually-hidden">{t('common.loading')}</span>
                </Spinner>
                <h4>{t('auth.verifyingEmail')}</h4>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  if (verificationStatus === 'success') {
    return (
      <Container>
        <Row className="justify-content-center mt-5">
          <Col md={6} lg={5}>
            <Card>
              <Card.Body>
                <h2 className="text-center mb-4">{t('auth.emailVerified')}</h2>
                <Alert variant="success">
                  <p>{t('auth.emailVerifiedMessage')}</p>
                </Alert>
                <div className="text-center">
                  <Link to="/login" className="btn btn-primary">
                    {t('auth.goToLogin')}
                  </Link>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  if (verificationStatus === 'no-token') {
    return (
      <Container>
        <Row className="justify-content-center mt-5">
          <Col md={6} lg={5}>
            <Card>
              <Card.Body>
                <h2 className="text-center mb-4">{t('auth.resendVerification')}</h2>

                {resendSuccess ? (
                  <Alert variant="success">
                    <p>{t('auth.verificationEmailResent')}</p>
                    <p>{t('auth.checkYourEmail')}</p>
                  </Alert>
                ) : (
                  <>
                    {error && (
                      <Alert variant="danger" dismissible onClose={() => dispatch(clearError())}>
                        {error.message || t('auth.errors.resendFailed')}
                      </Alert>
                    )}

                    <form onSubmit={handleResend}>
                      <div className="mb-3">
                        <label htmlFor="email" className="form-label">
                          {t('auth.email')}
                        </label>
                        <input
                          type="email"
                          className="form-control"
                          id="email"
                          value={resendEmail}
                          onChange={(e) => setResendEmail(e.target.value)}
                          required
                          placeholder={t('auth.emailPlaceholder')}
                        />
                      </div>
                      <Button variant="primary" type="submit" disabled={loading} className="w-100">
                        {loading ? t('common.loading') : t('auth.sendVerificationEmail')}
                      </Button>
                    </form>
                  </>
                )}

                <div className="text-center mt-3">
                  <Link to="/login">{t('auth.backToLogin')}</Link>
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
              <h2 className="text-center mb-4">{t('auth.verificationFailed')}</h2>
              <Alert variant="danger">
                <p>{error?.message || t('auth.verificationFailedMessage')}</p>
              </Alert>
              <div className="text-center">
                <Link to="/verify-email" className="btn btn-secondary me-2">
                  {t('auth.resendVerification')}
                </Link>
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
};

export default VerifyEmailPage;
