import React from 'react';
import { Container } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../common/LanguageSwitcher';

/**
 * PublicLayout component
 * Minimal layout for public pages (auth, ticket submission/view)
 */
const PublicLayout = ({ children, centered = false, maxWidth = 'md' }) => {
  const { t } = useTranslation();

  return (
    <div className="public-layout min-vh-100 d-flex flex-column bg-light">
      {/* Header */}
      <header className="bg-white border-bottom py-3">
        <Container>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h4 className="mb-0">
                <i className="bi bi-ticket-detailed me-2" />
                {t('app.title') || 'Simple Issue Tracker'}
              </h4>
            </div>
            <LanguageSwitcher />
          </div>
        </Container>
      </header>

      {/* Main Content */}
      <main className={`flex-grow-1 ${centered ? 'd-flex align-items-center' : 'py-5'}`}>
        <Container>
          <div className={`mx-auto ${maxWidth === 'sm' ? 'col-md-6' : maxWidth === 'md' ? 'col-lg-8' : 'col-lg-10'}`}>
            {children}
          </div>
        </Container>
      </main>

      {/* Footer */}
      <footer className="bg-white border-top py-3 mt-auto">
        <Container>
          <div className="text-center text-muted">
            <small>{t('app.tagline') || 'Manage ticket boards and track issues'}</small>
          </div>
        </Container>
      </footer>
    </div>
  );
};

export default PublicLayout;
