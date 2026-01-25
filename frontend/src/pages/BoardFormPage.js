import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { fetchBoard, createBoard, updateBoard } from '../store/slices/boardsSlice';
import ManagerLayout from '../components/layout/ManagerLayout';
import Card from '../components/common/Card';
import Spinner from '../components/common/Spinner';
import Alert from '../components/common/Alert';
import BoardForm from '../components/boards/BoardForm';

const BoardFormPage = () => {
  const { t } = useTranslation();
  const { boardId } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { currentBoard, loading, error } = useSelector((state) => state.boards);

  const isEditMode = !!boardId;

  useEffect(() => {
    if (isEditMode) {
      dispatch(fetchBoard(boardId));
    }
  }, [dispatch, boardId, isEditMode]);

  const breadcrumbs = [
    { label: t('nav.dashboard') || 'Dashboard', path: '/dashboard' },
    { label: t('nav.boards') || 'Boards', path: '/boards' },
    { label: isEditMode ? t('boards.edit') || 'Edit Board' : t('boards.create') || 'Create Board' }
  ];

  const handleSubmit = async (values) => {
    try {
      if (isEditMode) {
        await dispatch(updateBoard({ boardId, boardData: values })).unwrap();
      } else {
        await dispatch(createBoard(values)).unwrap();
      }
      navigate('/boards');
    } catch (err) {
      console.error('Failed to save board:', err);
    }
  };

  if (isEditMode && loading && !currentBoard) {
    return (
      <ManagerLayout breadcrumbs={breadcrumbs}>
        <Spinner fullPage message={t('common.loading')} />
      </ManagerLayout>
    );
  }

  return (
    <ManagerLayout breadcrumbs={breadcrumbs}>
      <div className="mb-4">
        <h1>{isEditMode ? t('boards.edit') || 'Edit Board' : t('boards.create') || 'Create Board'}</h1>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error.message || t('boards.errors.saveFailed')}
        </Alert>
      )}

      <Card className="col-lg-8">
        <BoardForm
          initialValues={isEditMode ? currentBoard : {}}
          onSubmit={handleSubmit}
          loading={loading}
        />
      </Card>
    </ManagerLayout>
  );
};

export default BoardFormPage;
