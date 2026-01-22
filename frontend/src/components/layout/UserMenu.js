import React from 'react';
import { Dropdown } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { logout } from '../../store/slices/authSlice';

/**
 * User menu dropdown component
 * Shows user profile and logout options
 */
const UserMenu = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const handleProfile = () => {
    navigate('/settings/profile');
  };

  return (
    <Dropdown align="end">
      <Dropdown.Toggle variant="outline-secondary" id="user-menu-dropdown">
        <i className="bi bi-person-circle me-2" />
        {user?.name || user?.email || 'User'}
      </Dropdown.Toggle>

      <Dropdown.Menu>
        <Dropdown.Item onClick={handleProfile}>
          <i className="bi bi-person me-2" />
          {t('nav.profile') || 'Profile'}
        </Dropdown.Item>
        <Dropdown.Item onClick={() => navigate('/settings')}>
          <i className="bi bi-gear me-2" />
          {t('nav.settings') || 'Settings'}
        </Dropdown.Item>
        <Dropdown.Divider />
        <Dropdown.Item onClick={handleLogout}>
          <i className="bi bi-box-arrow-right me-2" />
          {t('auth.logout') || 'Logout'}
        </Dropdown.Item>
      </Dropdown.Menu>
    </Dropdown>
  );
};

export default UserMenu;
