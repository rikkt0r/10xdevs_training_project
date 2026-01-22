import api from './api';

/**
 * Settings service for user profile and account management
 */
const settingsService = {
  /**
   * Get current user profile
   */
  getProfile: async () => {
    const response = await api.get('/me');
    return response.data;
  },

  /**
   * Update user profile (name, timezone)
   */
  updateProfile: async (profileData) => {
    const response = await api.patch('/me', profileData);
    return response.data;
  },

  /**
   * Change password
   */
  changePassword: async (currentPassword, newPassword) => {
    const response = await api.put('/me/password', {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response.data;
  },

  /**
   * Suspend account
   */
  suspendAccount: async (suspensionMessage, password) => {
    const response = await api.post('/me/suspend', {
      suspension_message: suspensionMessage,
      password: password
    });
    return response.data;
  },

  /**
   * Request account data export
   */
  exportAccountData: async () => {
    const response = await api.get('/me/export', {
      responseType: 'blob'
    });
    return response.data;
  }
};

export default settingsService;
