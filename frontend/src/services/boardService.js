import api from './api';

/**
 * Transform board data from backend format to frontend format
 */
const transformBoardData = (board) => {
  if (!board) return board;

  // Extract external platform config fields
  const config = board.external_platform_config || {};
  const platformFields = {};

  if (board.external_platform_type === 'jira') {
    platformFields.jira_url = config.jira_url || '';
    platformFields.jira_email = config.jira_email || '';
    platformFields.jira_api_token = config.jira_api_token || '';
    platformFields.external_project_key = config.project_key || '';
  } else if (board.external_platform_type === 'trello') {
    platformFields.trello_api_key = config.trello_api_key || '';
    platformFields.trello_token = config.trello_token || '';
    platformFields.external_board_id = config.board_id || '';
  }

  return {
    ...board,
    greeting: board.greeting_message,
    archived: board.is_archived,
    external_platform: board.external_platform_type,
    ...platformFields
  };
};

/**
 * Transform array of boards
 */
const transformBoardsArray = (boards) => {
  if (!Array.isArray(boards)) return boards;
  return boards.map(transformBoardData);
};

/**
 * Board service for board management operations
 */
const boardService = {
  /**
   * Get all boards for the current manager
   */
  getBoards: async () => {
    const response = await api.get('/boards');
    const boards = response.data.data;
    return transformBoardsArray(boards);
  },

  /**
   * Get a single board by ID
   */
  getBoard: async (boardId) => {
    const response = await api.get(`/boards/${boardId}`);
    const board = response.data.data;
    return transformBoardData(board);
  },

  /**
   * Create a new board
   */
  createBoard: async (boardData) => {
    // Build external_platform_config from individual fields
    let externalConfig = null;
    if (boardData.external_platform === 'jira') {
      externalConfig = {
        jira_url: boardData.jira_url,
        jira_email: boardData.jira_email,
        jira_api_token: boardData.jira_api_token,
        project_key: boardData.external_project_key
      };
    } else if (boardData.external_platform === 'trello') {
      externalConfig = {
        trello_api_key: boardData.trello_api_key,
        trello_token: boardData.trello_token,
        board_id: boardData.external_board_id
      };
    }

    // Transform frontend field names to backend format
    const backendData = {
      name: boardData.name,
      unique_name: boardData.unique_name,
      greeting_message: boardData.greeting || null,
      external_platform_type: boardData.external_platform || null,
      external_platform_config: externalConfig
    };

    const response = await api.post('/boards', backendData);
    const board = response.data.data;
    return transformBoardData(board);
  },

  /**
   * Update an existing board
   */
  updateBoard: async (boardId, boardData) => {
    // Build external_platform_config from individual fields
    let externalConfig = null;
    if (boardData.external_platform === 'jira') {
      externalConfig = {
        jira_url: boardData.jira_url,
        jira_email: boardData.jira_email,
        jira_api_token: boardData.jira_api_token,
        project_key: boardData.external_project_key
      };
    } else if (boardData.external_platform === 'trello') {
      externalConfig = {
        trello_api_key: boardData.trello_api_key,
        trello_token: boardData.trello_token,
        board_id: boardData.external_board_id
      };
    }

    // Transform frontend field names to backend format
    const backendData = {
      name: boardData.name,
      unique_name: boardData.unique_name,
      greeting_message: boardData.greeting || null,
      external_platform_type: boardData.external_platform || null,
      external_platform_config: externalConfig
    };

    const response = await api.put(`/boards/${boardId}`, backendData);
    const board = response.data.data;
    return transformBoardData(board);
  },

  /**
   * Archive a board
   */
  archiveBoard: async (boardId) => {
    const response = await api.post(`/boards/${boardId}/archive`);
    const board = response.data.data;
    return transformBoardData(board);
  },

  /**
   * Delete a board
   */
  deleteBoard: async (boardId) => {
    const response = await api.delete(`/boards/${boardId}`);
    return response.data; // DELETE returns 204 No Content
  },

  /**
   * Get keywords for a board
   */
  getKeywords: async (boardId) => {
    const response = await api.get(`/boards/${boardId}/keywords`);
    return response.data.data; // Extract data from DataResponse wrapper
  },

  /**
   * Add keyword to board
   */
  addKeyword: async (boardId, keyword) => {
    const response = await api.post(`/boards/${boardId}/keywords`, { keyword });
    return response.data.data; // Extract data from DataResponse wrapper
  },

  /**
   * Remove keyword from board
   */
  removeKeyword: async (boardId, keywordId) => {
    const response = await api.delete(`/boards/${boardId}/keywords/${keywordId}`);
    return response.data; // DELETE returns 204 No Content
  },

  /**
   * Test external platform connection
   */
  testExternalConnection: async (boardId) => {
    const response = await api.post(`/boards/${boardId}/test-external`);
    return response.data.data; // Extract data from DataResponse wrapper
  }
};

export default boardService;
