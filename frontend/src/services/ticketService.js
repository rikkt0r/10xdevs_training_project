import api from './api';

/**
 * Ticket service for ticket management operations
 */
const ticketService = {
  /**
   * Get tickets with optional filters
   * Returns PaginatedDataResponse
   */
  getTickets: async (params = {}) => {
    const response = await api.get('/tickets/recent', { params });
    return response.data; // PaginatedDataResponse has {data, pagination} at top level
  },

  /**
   * Get a single ticket by ID
   */
  getTicket: async (ticketId) => {
    const response = await api.get(`/tickets/${ticketId}`);
    return response.data.data; // Extract data from DataResponse wrapper
  },

  /**
   * Get tickets for a specific board
   * Returns PaginatedDataResponse
   */
  getBoardTickets: async (boardId, params = {}) => {
    const response = await api.get(`/boards/${boardId}/tickets`, { params });
    return response.data; // PaginatedDataResponse has {data, pagination} at top level
  },

  /**
   * Change ticket state
   */
  changeTicketState: async (ticketId, newState, comment = '') => {
    const response = await api.post(`/tickets/${ticketId}/state`, {
      new_state: newState,
      comment
    });
    return response.data.data; // Extract data from DataResponse wrapper
  },

  /**
   * Get ticket status history
   */
  getTicketHistory: async (ticketId) => {
    const response = await api.get(`/tickets/${ticketId}/history`);
    return response.data.data; // Extract data from DataResponse wrapper
  },

  /**
   * Delete a ticket
   */
  deleteTicket: async (ticketId) => {
    const response = await api.delete(`/tickets/${ticketId}`);
    return response.data; // DELETE returns 204 No Content
  }
};

export default ticketService;
