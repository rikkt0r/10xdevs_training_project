import api from './api';

/**
 * Settings service for user profile and account management
 */
const settingsService = {
  /**
   * Get current user profile
   */
  getProfile: async () => {
    const response = await api.get('/managers/me');
    return response.data;
  },

  /**
   * Update user profile
   */
  updateProfile: async (profileData) => {
    const response = await api.put('/managers/me', profileData);
    return response.data;
  },

  /**
   * Change password
   */
  changePassword: async (currentPassword, newPassword) => {
    const response = await api.post('/managers/me/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response.data;
  },

  /**
   * Suspend account
   */
  suspendAccount: async () => {
    const response = await api.post('/managers/me/suspend');
    return response.data;
  },

  /**
   * Request account data export
   */
  exportAccountData: async () => {
    const response = await api.get('/managers/me/export', {
      responseType: 'blob'
    });
    return response.data;
  }
};

export default settingsService;
