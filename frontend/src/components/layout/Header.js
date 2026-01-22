import React from 'react';
import LanguageSwitcher from '../common/LanguageSwitcher';
import UserMenu from './UserMenu';

/**
 * Header component for manager area
 * Top bar with language switcher and user menu
 */
const Header = ({ sidebarCollapsed = false }) => {
  return (
    <header
      className="bg-white border-bottom"
      style={{
        height: '60px',
        position: 'fixed',
        top: 0,
        right: 0,
        left: sidebarCollapsed ? '60px' : '250px',
        transition: 'left 0.3s ease',
        zIndex: 999
      }}
    >
      <div className="h-100 px-4 d-flex align-items-center justify-content-end">
        <div className="d-flex align-items-center gap-3">
          <LanguageSwitcher />
          <UserMenu />
        </div>
      </div>
    </header>
  );
};

export default Header;
