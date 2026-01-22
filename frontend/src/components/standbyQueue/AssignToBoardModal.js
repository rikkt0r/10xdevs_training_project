import React, { useState } from 'react';
import { Form } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import Modal from '../common/Modal';
import Select from '../common/Select';
import FormGroup from '../common/FormGroup';

/**
 * AssignToBoardModal component
 * Modal for selecting a board to assign a queue item to
 */
const AssignToBoardModal = ({
  show,
  onHide,
  boards,
  onConfirm,
  loading = false,
}) => {
  const { t } = useTranslation();
  const [selectedBoardId, setSelectedBoardId] = useState('');
  const [error, setError] = useState('');

  const handleConfirm = async () => {
    if (!selectedBoardId) {
      setError(t('standbyQueue.errors.boardRequired') || 'Please select a board');
      return;
    }

    try {
      await onConfirm(selectedBoardId);
      setSelectedBoardId('');
      setError('');
    } catch (err) {
      // Error handling is done by parent component
    }
  };

  const handleClose = () => {
    setSelectedBoardId('');
    setError('');
    onHide();
  };

  const boardOptions = [
    { value: '', label: t('standbyQueue.selectBoard') || 'Select a board...' },
    ...boards
      .filter(board => !board.archived)
      .map(board => ({
        value: board.id,
        label: board.name,
      }))
  ];

  return (
    <Modal
      show={show}
      onHide={handleClose}
      title={t('standbyQueue.assignToBoard') || 'Assign to Board'}
      confirmLabel={t('standbyQueue.assign') || 'Assign'}
      cancelLabel={t('common.cancel') || 'Cancel'}
      onConfirm={handleConfirm}
      loading={loading}
    >
      <Form>
        <FormGroup
          label={t('standbyQueue.board') || 'Board'}
          error={error}
          required
          htmlFor="board"
          helpText={t('standbyQueue.assignHelp') || 'Select which board this ticket should be assigned to'}
        >
          <Select
            id="board"
            name="board"
            value={selectedBoardId}
            onChange={(e) => {
              setSelectedBoardId(e.target.value);
              setError('');
            }}
            options={boardOptions}
            error={error}
          />
        </FormGroup>

        {selectedBoardId && (
          <div className="alert alert-info mb-0">
            <i className="bi bi-info-circle me-2" />
            {t('standbyQueue.assignNote') || 'This will create a ticket on the selected board and remove the item from the queue.'}
          </div>
        )}
      </Form>
    </Modal>
  );
};

export default AssignToBoardModal;
