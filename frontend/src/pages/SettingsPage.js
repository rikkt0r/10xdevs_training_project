import React from 'react';
import { Link } from 'react-router-dom';
import { Row, Col } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import ManagerLayout from '../components/layout/ManagerLayout';
import Card from '../components/common/Card';

const SettingsPage = () => {
  const { t } = useTranslation();

  const breadcrumbs = [
    { label: t('nav.dashboard') || 'Dashboard', path: '/dashboard' },
    { label: t('nav.settings') || 'Settings' }
  ];

  const settingsCategories = [
    {
      icon: 'bi-person',
      title: t('settings.profile') || 'Profile',
      description: t('settings.profileDescription') || 'Manage your account information',
      path: '/settings/profile'
    },
    {
      icon: 'bi-shield-lock',
      title: t('settings.security') || 'Security',
      description: t('settings.securityDescription') || 'Manage your password and account security',
      path: '/settings/security'
    },
    {
      icon: 'bi-inbox',
      title: t('settings.inboxes') || 'Email Inboxes',
      description: t('settings.inboxesDescription') || 'Configure email accounts for receiving tickets',
      path: '/settings/inboxes'
    }
  ];

  return (
    <ManagerLayout breadcrumbs={breadcrumbs}>
      <div className="mb-4">
        <h1>{t('nav.settings') || 'Settings'}</h1>
        <p className="text-muted">
          {t('settings.pageDescription') || 'Manage your account and application settings'}
        </p>
      </div>

      <Row>
        {settingsCategories.map((category) => (
          <Col key={category.path} lg={4} md={6} className="mb-4">
            <Link to={category.path} className="text-decoration-none">
              <Card className="h-100 settings-card">
                <div className="d-flex flex-column h-100">
                  <div className="mb-3">
                    <i className={`${category.icon} fs-1 text-primary`} />
                  </div>
                  <h5 className="mb-2">{category.title}</h5>
                  <p className="text-muted mb-0 flex-grow-1">{category.description}</p>
                  <div className="mt-3">
                    <span className="text-primary">
                      {t('common.viewMore') || 'View more'}{' '}
                      <i className="bi bi-arrow-right" />
                    </span>
                  </div>
                </div>
              </Card>
            </Link>
          </Col>
        ))}
      </Row>

      <style jsx="true">{`
        .settings-card {
          transition: all 0.2s ease-in-out;
          cursor: pointer;
        }

        .settings-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        a:hover .settings-card {
          border-color: var(--bs-primary);
        }
      `}</style>
    </ManagerLayout>
  );
};

export default SettingsPage;
