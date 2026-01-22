import React, { useState } from 'react';
import { Container } from 'react-bootstrap';
import Sidebar from './Sidebar';
import Header from './Header';
import Breadcrumbs from '../common/Breadcrumbs';

/**
 * ManagerLayout component
 * Main layout for authenticated manager area with sidebar and header
 */
const ManagerLayout = ({ children, breadcrumbs = [] }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleToggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <div className="manager-layout">
      <Sidebar collapsed={sidebarCollapsed} onToggle={handleToggleSidebar} />
      <Header sidebarCollapsed={sidebarCollapsed} />

      <main
        style={{
          marginLeft: sidebarCollapsed ? '60px' : '250px',
          marginTop: '60px',
          transition: 'margin-left 0.3s ease',
          minHeight: 'calc(100vh - 60px)',
          backgroundColor: '#f8f9fa'
        }}
      >
        <Container fluid className="py-4">
          {breadcrumbs && breadcrumbs.length > 0 && (
            <Breadcrumbs items={breadcrumbs} className="mb-3" />
          )}
          {children}
        </Container>
      </main>
    </div>
  );
};

export default ManagerLayout;
