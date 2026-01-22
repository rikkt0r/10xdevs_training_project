import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Form, Button, Card, Alert, Container, Row, Col, Spinner } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import * as publicService from '../services/publicService';

const PublicTicketFormPage = () => {
  const { t } = useTranslation();
  const { uniqueName } = useParams();

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [boardInfo, setBoardInfo] = useState(null);
  const [error, setError] = useState(null);
  const [ticketCreated, setTicketCreated] = useState(null);

  const [formData, setFormData] = useState({
    email: '',
    title: '',
    description: '',
  });

  const [validationErrors, setValidationErrors] = useState({});

  useEffect(() => {
    const loadBoardInfo = async () => {
      try {
        setLoading(true);
        const response = await publicService.getBoardInfo(uniqueName);
        setBoardInfo(response.data.data);
        setError(null);
      } catch (err) {
        if (err.response?.status === 404) {
          setError({
            type: 'not_found',
            message: t('public.errors.boardNotFound'),
          });
        } else if (err.response?.status === 410) {
          setError({
            type: 'archived',
            message: t('public.errors.boardArchived'),
          });
        } else if (err.response?.status === 403) {
          const errorData = err.response.data?.error;
          setError({
            type: 'suspended',
            message: errorData?.message || t('public.errors.managerSuspended'),
          });
        } else {
          setError({
            type: 'unknown',
            message: t('public.errors.loadBoardFailed'),
          });
        }
      } finally {
        setLoading(false);
      }
    };

    loadBoardInfo();
  }, [uniqueName, t]);

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
      errors.email = t('public.errors.emailRequired');
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = t('public.errors.emailInvalid');
    }

    if (!formData.title) {
      errors.title = t('public.errors.titleRequired');
    } else if (formData.title.length > 255) {
      errors.title = t('public.errors.titleTooLong');
    }

    if (!formData.description) {
      errors.description = t('public.errors.descriptionRequired');
    } else if (formData.description.length > 6000) {
      errors.description = t('public.errors.descriptionTooLong');
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setSubmitting(true);
      const response = await publicService.createPublicTicket(uniqueName, formData);
      setTicketCreated(response.data.data);
      setFormData({ email: '', title: '', description: '' });
    } catch (err) {
      if (err.response?.status === 404) {
        setError({
          type: 'not_found',
          message: t('public.errors.boardNotFound'),
        });
      } else if (err.response?.status === 410) {
        setError({
          type: 'archived',
          message: t('public.errors.boardArchived'),
        });
      } else if (err.response?.status === 403) {
        const errorData = err.response.data?.error;
        setError({
          type: 'suspended',
          message: errorData?.message || t('public.errors.managerSuspended'),
        });
      } else {
        setError({
          type: 'submit_failed',
          message: err.response?.data?.error?.message || t('public.errors.createTicketFailed'),
        });
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Container>
        <Row className="justify-content-center mt-5">
          <Col md={8} lg={6}>
            <div className="text-center">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">{t('common.loading')}</span>
              </Spinner>
            </div>
          </Col>
        </Row>
      </Container>
    );
  }

  if (error && (error.type === 'not_found' || error.type === 'archived' || error.type === 'suspended')) {
    return (
      <Container>
        <Row className="justify-content-center mt-5">
          <Col md={8} lg={6}>
            <Card>
              <Card.Body>
                <h2 className="text-center mb-4">{t('public.boardUnavailable')}</h2>
                <Alert variant={error.type === 'archived' ? 'warning' : 'danger'}>
                  {error.message}
                </Alert>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  if (ticketCreated) {
    return (
      <Container>
        <Row className="justify-content-center mt-5">
          <Col md={8} lg={6}>
            <Card>
              <Card.Body>
                <h2 className="text-center mb-4">{t('public.ticketCreated')}</h2>
                <Alert variant="success">
                  <p className="mb-2">{ticketCreated.message}</p>
                  <p className="mb-0">
                    <strong>{t('public.ticketNumber')}:</strong> {ticketCreated.uuid}
                  </p>
                </Alert>
                <div className="text-center mt-3">
                  <Link to={`/ticket/${ticketCreated.uuid}`} className="btn btn-primary me-2">
                    {t('public.viewTicket')}
                  </Link>
                  <Button variant="secondary" onClick={() => setTicketCreated(null)}>
                    {t('public.createAnother')}
                  </Button>
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
        <Col md={8} lg={6}>
          <Card>
            <Card.Body>
              <h2 className="text-center mb-4">{boardInfo?.name || t('public.createTicket')}</h2>

              {boardInfo?.greeting_message && (
                <Alert variant="info" className="mb-4">
                  {boardInfo.greeting_message}
                </Alert>
              )}

              {error && error.type === 'submit_failed' && (
                <Alert variant="danger" dismissible onClose={() => setError(null)}>
                  {error.message}
                </Alert>
              )}

              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3" controlId="email">
                  <Form.Label>{t('public.email')}</Form.Label>
                  <Form.Control
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    isInvalid={!!validationErrors.email}
                    placeholder={t('public.emailPlaceholder')}
                  />
                  <Form.Control.Feedback type="invalid">
                    {validationErrors.email}
                  </Form.Control.Feedback>
                </Form.Group>

                <Form.Group className="mb-3" controlId="title">
                  <Form.Label>{t('public.title')}</Form.Label>
                  <Form.Control
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleChange}
                    isInvalid={!!validationErrors.title}
                    placeholder={t('public.titlePlaceholder')}
                    maxLength={255}
                  />
                  <Form.Control.Feedback type="invalid">
                    {validationErrors.title}
                  </Form.Control.Feedback>
                  <Form.Text className="text-muted">
                    {formData.title.length}/255
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3" controlId="description">
                  <Form.Label>{t('public.description')}</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={6}
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    isInvalid={!!validationErrors.description}
                    placeholder={t('public.descriptionPlaceholder')}
                    maxLength={6000}
                  />
                  <Form.Control.Feedback type="invalid">
                    {validationErrors.description}
                  </Form.Control.Feedback>
                  <Form.Text className="text-muted">
                    {formData.description.length}/6000
                  </Form.Text>
                </Form.Group>

                <Button variant="primary" type="submit" disabled={submitting} className="w-100">
                  {submitting ? t('common.loading') : t('public.submitTicket')}
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default PublicTicketFormPage;
