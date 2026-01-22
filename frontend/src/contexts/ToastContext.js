import React, { createContext, useContext, useState, useCallback } from 'react';
import { ToastContainer } from 'react-bootstrap';
import Toast from '../components/common/Toast';

const ToastContext = createContext();

/**
 * Hook to use toast notifications
 * @returns {Object} Toast context methods
 */
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

/**
 * ToastProvider component
 * Manages toast notifications with max 3 toasts at a time
 */
export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);
  const MAX_TOASTS = 3;

  /**
   * Add a new toast notification
   * @param {string} message - Toast message
   * @param {Object} options - Toast options (variant, title, autoHide, delay)
   */
  const showToast = useCallback((message, options = {}) => {
    const id = Date.now() + Math.random();
    const newToast = {
      id,
      message,
      variant: options.variant || 'info',
      title: options.title || '',
      autoHide: options.autoHide !== undefined ? options.autoHide : true,
      delay: options.delay || 5000,
    };

    setToasts((prevToasts) => {
      const updatedToasts = [...prevToasts, newToast];
      // Keep only the last MAX_TOASTS toasts
      return updatedToasts.slice(-MAX_TOASTS);
    });

    return id;
  }, []);

  /**
   * Remove a toast by ID
   * @param {number} id - Toast ID
   */
  const removeToast = useCallback((id) => {
    setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id));
  }, []);

  /**
   * Convenience methods for different toast variants
   */
  const success = useCallback(
    (message, options = {}) => {
      return showToast(message, { ...options, variant: 'success' });
    },
    [showToast]
  );

  const error = useCallback(
    (message, options = {}) => {
      return showToast(message, { ...options, variant: 'danger' });
    },
    [showToast]
  );

  const warning = useCallback(
    (message, options = {}) => {
      return showToast(message, { ...options, variant: 'warning' });
    },
    [showToast]
  );

  const info = useCallback(
    (message, options = {}) => {
      return showToast(message, { ...options, variant: 'info' });
    },
    [showToast]
  );

  const contextValue = {
    showToast,
    removeToast,
    success,
    error,
    warning,
    info,
  };

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      <ToastContainer
        position="top-end"
        className="p-3"
        style={{
          position: 'fixed',
          zIndex: 9999,
        }}
      >
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            show={true}
            onClose={() => removeToast(toast.id)}
            message={toast.message}
            title={toast.title}
            variant={toast.variant}
            autoHide={toast.autoHide}
            delay={toast.delay}
          />
        ))}
      </ToastContainer>
    </ToastContext.Provider>
  );
};

export default ToastContext;
