import api from './api';

/**
 * Standby queue service for managing queue items
 */
const standbyQueueService = {
  /**
   * Get all standby queue items
   */
  getQueueItems: async (params = {}) => {
    const response = await api.get('/standby-queue', { params });
    return response.data;
  },

  /**
   * Get a single queue item by ID
   */
  getQueueItem: async (itemId) => {
    const response = await api.get(`/standby-queue/${itemId}`);
    return response.data;
  },

  /**
   * Assign queue item to a board
   */
  assignToBoard: async (itemId, boardId) => {
    const response = await api.post(`/standby-queue/${itemId}/assign`, {
      board_id: boardId
    });
    return response.data;
  },

  /**
   * Retry external platform sync for a queue item
   */
  retryExternal: async (itemId) => {
    const response = await api.post(`/standby-queue/${itemId}/retry`);
    return response.data;
  },

  /**
   * Discard a queue item
   */
  discardItem: async (itemId) => {
    const response = await api.delete(`/standby-queue/${itemId}`);
    return response.data;
  }
};

export default standbyQueueService;
