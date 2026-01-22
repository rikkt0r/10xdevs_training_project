import React from 'react';
import { Modal as BootstrapModal } from 'react-bootstrap';
import Button from './Button';

/**
 * Reusable Modal component
 * Standard and danger confirmation variants
 */
const Modal = ({
  show = false,
  onHide,
  title,
  children,
  footer,
  size = 'md',
  centered = true,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
  confirmVariant = 'primary',
  showFooter = true,
  loading = false,
  className = '',
}) => {
  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      onHide();
    }
  };

  return (
    <BootstrapModal
      show={show}
      onHide={onHide}
      size={size}
      centered={centered}
      className={className}
      backdrop={loading ? 'static' : true}
      keyboard={!loading}
    >
      {title && (
        <BootstrapModal.Header closeButton={!loading}>
          <BootstrapModal.Title>{title}</BootstrapModal.Title>
        </BootstrapModal.Header>
      )}

      <BootstrapModal.Body>{children}</BootstrapModal.Body>

      {showFooter && (
        <BootstrapModal.Footer>
          {footer || (
            <>
              <Button
                variant="secondary"
                onClick={handleCancel}
                disabled={loading}
              >
                {cancelLabel}
              </Button>
              {onConfirm && (
                <Button
                  variant={confirmVariant}
                  onClick={onConfirm}
                  loading={loading}
                  disabled={loading}
                >
                  {confirmLabel}
                </Button>
              )}
            </>
          )}
        </BootstrapModal.Footer>
      )}
    </BootstrapModal>
  );
};

export default Modal;
