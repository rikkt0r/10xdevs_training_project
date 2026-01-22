import React, { useState } from 'react';
import { Form } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import Modal from '../common/Modal';
import Textarea from '../common/Textarea';
import Badge from '../common/Badge';
import FormGroup from '../common/FormGroup';
import { getStateLabel, getStateBadgeVariant } from '../../utils/ticketUtils';

/**
 * StateChangeModal component
 * Modal for changing ticket state with optional comment
 */
const StateChangeModal = ({
  show,
  onHide,
  currentState,
  newState,
  onConfirm,
}) => {
  const { t } = useTranslation();
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);

  const handleConfirm = async () => {
    setLoading(true);
    try {
      await onConfirm(comment);
      setComment('');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setComment('');
    onHide();
  };

  return (
    <Modal
      show={show}
      onHide={handleClose}
      title={t('tickets.changeState') || 'Change Ticket State'}
      confirmLabel={t('tickets.confirmStateChange') || 'Change State'}
      cancelLabel={t('common.cancel') || 'Cancel'}
      onConfirm={handleConfirm}
      loading={loading}
    >
      <div className="mb-3">
        <p className="mb-2">{t('tickets.stateChangeConfirm') || 'Change ticket state from:'}</p>
        <div className="d-flex align-items-center gap-2">
          <Badge variant={getStateBadgeVariant(currentState)}>
            {getStateLabel(currentState, t)}
          </Badge>
          <i className="bi bi-arrow-right" />
          <Badge variant={getStateBadgeVariant(newState)}>
            {getStateLabel(newState, t)}
          </Badge>
        </div>
      </div>

      <Form>
        <FormGroup
          label={t('tickets.comment') || 'Comment (Optional)'}
          helpText={t('tickets.commentHelp') || 'Add a comment about this state change'}
          htmlFor="comment"
        >
          <Textarea
            id="comment"
            name="comment"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={4}
            placeholder={t('tickets.commentPlaceholder') || 'Enter comment...'}
          />
        </FormGroup>
      </Form>
    </Modal>
  );
};

export default StateChangeModal;
