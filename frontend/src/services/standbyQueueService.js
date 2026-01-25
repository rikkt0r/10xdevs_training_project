import api from './api';

/**
 * Standby queue service for managing queue items
 */
const standbyQueueService = {
  /**
   * Get all standby queue items
   * May return PaginatedDataResponse
   */
  getQueueItems: async (params = {}) => {
    const response = await api.get('/standby-queue', { params });
    return response.data; // PaginatedDataResponse has {data, pagination} at top level
  },

  /**
   * Get a single queue item by ID
   */
  getQueueItem: async (itemId) => {
    const response = await api.get(`/standby-queue/${itemId}`);
    return response.data.data; // Extract data from DataResponse wrapper
  },

  /**
   * Assign queue item to a board
   */
  assignToBoard: async (itemId, boardId) => {
    const response = await api.post(`/standby-queue/${itemId}/assign`, {
      board_id: boardId
    });
    return response.data.data; // Extract data from DataResponse wrapper
  },

  /**
   * Retry external platform sync for a queue item
   */
  retryExternal: async (itemId) => {
    const response = await api.post(`/standby-queue/${itemId}/retry`);
    return response.data.data; // Extract data from DataResponse wrapper
  },

  /**
   * Discard a queue item
   */
  discardItem: async (itemId) => {
    const response = await api.delete(`/standby-queue/${itemId}`);
    return response.data; // DELETE returns 204 No Content
  }
};

export default standbyQueueService;
