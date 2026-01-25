import api from './api';

/**
 * Inbox service for email inbox configuration
 */
const inboxService = {
  /**
   * Get all configured inboxes
   */
  getInboxes: async () => {
    const response = await api.get('/inboxes');
    return response.data.data; // Extract data from DataResponse wrapper
  },

  /**
   * Get a single inbox by ID
   */
  getInbox: async (inboxId) => {
    const response = await api.get(`/inboxes/${inboxId}`);
    return response.data.data; // Extract data from DataResponse wrapper
  },

  /**
   * Create a new inbox
   */
  createInbox: async (inboxData) => {
    const response = await api.post('/inboxes', inboxData);
    return response.data.data; // Extract data from DataResponse wrapper
  },

  /**
   * Update an existing inbox
   */
  updateInbox: async (inboxId, inboxData) => {
    const response = await api.put(`/inboxes/${inboxId}`, inboxData);
    return response.data.data; // Extract data from DataResponse wrapper
  },

  /**
   * Delete an inbox
   */
  deleteInbox: async (inboxId) => {
    const response = await api.delete(`/inboxes/${inboxId}`);
    return response.data; // DELETE returns 204 No Content
  },

  /**
   * Test inbox connection
   */
  testConnection: async (inboxId) => {
    const response = await api.post(`/inboxes/${inboxId}/test`);
    return response.data.data; // Extract data from DataResponse wrapper
  },

  /**
   * Test inbox configuration before saving
   */
  testInboxConfig: async (inboxData) => {
    const response = await api.post('/inboxes/test', inboxData);
    return response.data.data; // Extract data from DataResponse wrapper
  }
};

export default inboxService;
