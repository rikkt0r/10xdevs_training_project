import React from 'react';
import Modal from './Modal';

/**
 * Simplified Confirmation Modal
 * Wrapper around Modal for common confirmation dialogs
 */
const ConfirmModal = ({
  show = false,
  onHide,
  title = 'Confirm Action',
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  onConfirm,
  variant = 'primary',
  loading = false,
  ...props
}) => {
  return (
    <Modal
      show={show}
      onHide={onHide}
      title={title}
      confirmLabel={confirmLabel}
      cancelLabel={cancelLabel}
      onConfirm={onConfirm}
      confirmVariant={variant}
      loading={loading}
      {...props}
    >
      <p className="mb-0">{message}</p>
    </Modal>
  );
};

export default ConfirmModal;
