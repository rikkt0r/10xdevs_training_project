import React from 'react';
import { Nav } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

/**
 * Sidebar navigation component for manager area
 */
const Sidebar = ({ collapsed = false, onToggle }) => {
  const { t } = useTranslation();
  const location = useLocation();

  const navItems = [
    {
      path: '/dashboard',
      icon: 'bi-speedometer2',
      label: t('nav.dashboard') || 'Dashboard'
    },
    {
      path: '/boards',
      icon: 'bi-kanban',
      label: t('nav.boards') || 'Boards'
    },
    {
      path: '/standby-queue',
      icon: 'bi-inbox',
      label: t('nav.standbyQueue') || 'Standby Queue'
    },
    {
      path: '/settings',
      icon: 'bi-gear',
      label: t('nav.settings') || 'Settings'
    }
  ];

  const isActive = (path) => {
    return location.pathname.startsWith(path);
  };

  return (
    <div
      className={`sidebar bg-dark text-white ${collapsed ? 'collapsed' : ''}`}
      style={{
        width: collapsed ? '60px' : '250px',
        minHeight: '100vh',
        transition: 'width 0.3s ease',
        position: 'fixed',
        top: 0,
        left: 0,
        zIndex: 1000
      }}
    >
      {/* Sidebar Header */}
      <div
        className="sidebar-header p-3 border-bottom border-secondary"
        style={{ height: '60px' }}
      >
        <div className="d-flex align-items-center justify-content-between">
          {!collapsed && (
            <h5 className="mb-0 text-truncate">
              <i className="bi bi-ticket-detailed me-2" />
              {t('app.title') || 'Issue Tracker'}
            </h5>
          )}
          <button
            className="btn btn-link text-white p-0"
            onClick={onToggle}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            <i className={`bi bi-${collapsed ? 'chevron-right' : 'chevron-left'}`} />
          </button>
        </div>
      </div>

      {/* Navigation Menu */}
      <Nav className="flex-column mt-3">
        {navItems.map((item) => (
          <Nav.Link
            key={item.path}
            as={Link}
            to={item.path}
            className={`text-white px-3 py-2 ${isActive(item.path) ? 'bg-primary' : ''}`}
            style={{
              borderLeft: isActive(item.path) ? '3px solid white' : 'none'
            }}
          >
            <i className={`${item.icon} fs-5`} />
            {!collapsed && <span className="ms-3">{item.label}</span>}
          </Nav.Link>
        ))}
      </Nav>
    </div>
  );
};

export default Sidebar;
