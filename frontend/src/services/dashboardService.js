import api from './api';

export const getDashboardStats = () => {
  return api.get('/dashboard/stats');
};

export const getRecentTickets = (limit = 10) => {
  return api.get('/tickets/recent', { params: { limit } });
};
