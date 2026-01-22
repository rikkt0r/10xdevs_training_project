import api from './api';

export const login = (email, password) => {
  return api.post('/auth/login', { email, password });
};

export const register = (email, password, name) => {
  return api.post('/auth/register', { email, password, name });
};

export const verifyEmail = (token) => {
  return api.post('/auth/verify-email', { token });
};

export const resendVerification = (email) => {
  return api.post('/auth/resend-verification', { email });
};

export const forgotPassword = (email) => {
  return api.post('/auth/forgot-password', { email });
};

export const resetPassword = (token, password) => {
  return api.post('/auth/reset-password', { token, password });
};

export const logout = () => {
  return api.post('/auth/logout');
};

export const refreshToken = () => {
  return api.post('/auth/refresh');
};

export const getProfile = () => {
  return api.get('/me');
};

export const updateProfile = (data) => {
  return api.patch('/me', data);
};

export const changePassword = (currentPassword, newPassword) => {
  return api.put('/me/password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
};

export const suspendAccount = (suspensionMessage, password) => {
  return api.post('/me/suspend', {
    suspension_message: suspensionMessage,
    password,
  });
};
