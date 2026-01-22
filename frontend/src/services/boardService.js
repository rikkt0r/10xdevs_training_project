import api from './api';

/**
 * Board service for board management operations
 */
const boardService = {
  /**
   * Get all boards for the current manager
   */
  getBoards: async () => {
    const response = await api.get('/boards');
    return response.data;
  },

  /**
   * Get a single board by ID
   */
  getBoard: async (boardId) => {
    const response = await api.get(`/boards/${boardId}`);
    return response.data;
  },

  /**
   * Create a new board
   */
  createBoard: async (boardData) => {
    const response = await api.post('/boards', boardData);
    return response.data;
  },

  /**
   * Update an existing board
   */
  updateBoard: async (boardId, boardData) => {
    const response = await api.put(`/boards/${boardId}`, boardData);
    return response.data;
  },

  /**
   * Archive a board
   */
  archiveBoard: async (boardId) => {
    const response = await api.post(`/boards/${boardId}/archive`);
    return response.data;
  },

  /**
   * Delete a board
   */
  deleteBoard: async (boardId) => {
    const response = await api.delete(`/boards/${boardId}`);
    return response.data;
  },

  /**
   * Get keywords for a board
   */
  getKeywords: async (boardId) => {
    const response = await api.get(`/boards/${boardId}/keywords`);
    return response.data;
  },

  /**
   * Add keyword to board
   */
  addKeyword: async (boardId, keyword) => {
    const response = await api.post(`/boards/${boardId}/keywords`, { keyword });
    return response.data;
  },

  /**
   * Remove keyword from board
   */
  removeKeyword: async (boardId, keywordId) => {
    const response = await api.delete(`/boards/${boardId}/keywords/${keywordId}`);
    return response.data;
  },

  /**
   * Test external platform connection
   */
  testExternalConnection: async (boardId) => {
    const response = await api.post(`/boards/${boardId}/test-external`);
    return response.data;
  }
};

export default boardService;
