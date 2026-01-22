import api from './api';

// These are public endpoints that don't require authentication
// We'll use the same axios instance but these endpoints won't need tokens

export const getBoardInfo = (uniqueName) => {
  return api.get(`/public/boards/${uniqueName}`);
};

export const createPublicTicket = (uniqueName, ticketData) => {
  return api.post(`/public/boards/${uniqueName}/tickets`, ticketData);
};

export const getPublicTicket = (uuid) => {
  return api.get(`/public/tickets/${uuid}`);
};
