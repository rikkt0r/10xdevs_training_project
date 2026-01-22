import api from './api';

/**
 * Ticket service for ticket management operations
 */
const ticketService = {
  /**
   * Get tickets with optional filters
   */
  getTickets: async (params = {}) => {
    const response = await api.get('/tickets', { params });
    return response.data;
  },

  /**
   * Get a single ticket by ID
   */
  getTicket: async (ticketId) => {
    const response = await api.get(`/tickets/${ticketId}`);
    return response.data;
  },

  /**
   * Get tickets for a specific board
   */
  getBoardTickets: async (boardId, params = {}) => {
    const response = await api.get(`/boards/${boardId}/tickets`, { params });
    return response.data;
  },

  /**
   * Change ticket state
   */
  changeTicketState: async (ticketId, newState, comment = '') => {
    const response = await api.post(`/tickets/${ticketId}/state`, {
      new_state: newState,
      comment
    });
    return response.data;
  },

  /**
   * Get ticket status history
   */
  getTicketHistory: async (ticketId) => {
    const response = await api.get(`/tickets/${ticketId}/history`);
    return response.data;
  },

  /**
   * Delete a ticket
   */
  deleteTicket: async (ticketId) => {
    const response = await api.delete(`/tickets/${ticketId}`);
    return response.data;
  }
};

export default ticketService;
