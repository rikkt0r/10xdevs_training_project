import { useState, useCallback } from 'react';

/**
 * Custom hook for managing toast notifications
 * Provides methods to show/hide toasts
 */
const useToast = () => {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message, options = {}) => {
    const {
      title = '',
      variant = 'info',
      autoHide = true,
      delay = 5000
    } = options;

    const id = Date.now() + Math.random();

    const toast = {
      id,
      message,
      title,
      variant,
      autoHide,
      delay,
      show: true
    };

    setToasts(prev => [...prev, toast]);

    // Auto-remove toast after delay
    if (autoHide) {
      setTimeout(() => {
        hideToast(id);
      }, delay);
    }

    return id;
  }, []);

  const hideToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const showSuccess = useCallback((message, title = 'Success') => {
    return showToast(message, { title, variant: 'success' });
  }, [showToast]);

  const showError = useCallback((message, title = 'Error') => {
    return showToast(message, { title, variant: 'danger', delay: 7000 });
  }, [showToast]);

  const showWarning = useCallback((message, title = 'Warning') => {
    return showToast(message, { title, variant: 'warning' });
  }, [showToast]);

  const showInfo = useCallback((message, title = 'Info') => {
    return showToast(message, { title, variant: 'info' });
  }, [showToast]);

  const clearAll = useCallback(() => {
    setToasts([]);
  }, []);

  return {
    toasts,
    showToast,
    hideToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    clearAll
  };
};

export default useToast;
