import React, { useState, useEffect } from 'react';
import { Row, Col } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { fetchTickets, setFilters, clearFilters } from '../store/slices/ticketsSlice';
import ManagerLayout from '../components/layout/ManagerLayout';
import Card from '../components/common/Card';
import Spinner from '../components/common/Spinner';
import EmptyState from '../components/common/EmptyState';
import Alert from '../components/common/Alert';
import FilterPanel from '../components/common/FilterPanel';
import Pagination from '../components/common/Pagination';
import Input from '../components/common/Input';
import Select from '../components/common/Select';
import FormGroup from '../components/common/FormGroup';
import TicketCard from '../components/tickets/TicketCard';
import usePagination from '../hooks/usePagination';
import useDebounce from '../hooks/useDebounce';
import { TICKET_STATES } from '../utils/ticketUtils';

const TicketListPage = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { tickets, loading, error, filters } = useSelector((state) => state.tickets);

  const [localSearch, setLocalSearch] = useState(filters.search || '');
  const debouncedSearch = useDebounce(localSearch, 500);

  const {
    currentPage,
    pageSize,
    handlePageChange,
    handlePageSizeChange,
    getPaginatedData,
    getPaginationMetadata
  } = usePagination(1, 10);

  useEffect(() => {
    dispatch(fetchTickets({
      state: filters.state,
      search: debouncedSearch,
    }));
  }, [dispatch, filters.state, debouncedSearch]);

  const breadcrumbs = [
    { label: t('nav.dashboard') || 'Dashboard', path: '/dashboard' },
    { label: t('tickets.allTickets') || 'All Tickets' }
  ];

  const handleFilterChange = (field, value) => {
    dispatch(setFilters({ [field]: value }));
  };

  const handleClearFilters = () => {
    dispatch(clearFilters());
    setLocalSearch('');
  };

  const stateOptions = [
    { value: '', label: t('tickets.allStates') || 'All States' },
    ...Object.keys(TICKET_STATES).map(state => ({
      value: state,
      label: t(`tickets.states.${state}`) || TICKET_STATES[state]
    }))
  ];

  const activeFiltersCount = [
    filters.state && 1,
    filters.search && 1,
  ].filter(Boolean).length;

  const paginatedTickets = getPaginatedData(tickets);
  const paginationMetadata = getPaginationMetadata(tickets.length);

  return (
    <ManagerLayout breadcrumbs={breadcrumbs}>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>{t('tickets.allTickets') || 'All Tickets'}</h1>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error.message || t('tickets.errors.loadFailed')}
        </Alert>
      )}

      <Row>
        <Col lg={3} className="mb-4">
          <FilterPanel
            activeFiltersCount={activeFiltersCount}
            onClear={handleClearFilters}
            defaultOpen={true}
          >
            <FormGroup label={t('tickets.search') || 'Search'} htmlFor="search">
              <Input
                type="text"
                id="search"
                name="search"
                value={localSearch}
                onChange={(e) => setLocalSearch(e.target.value)}
                placeholder={t('tickets.searchPlaceholder') || 'Search tickets...'}
              />
            </FormGroup>

            <FormGroup label={t('tickets.state') || 'State'} htmlFor="state">
              <Select
                id="state"
                name="state"
                value={filters.state}
                onChange={(e) => handleFilterChange('state', e.target.value)}
                options={stateOptions}
              />
            </FormGroup>
          </FilterPanel>
        </Col>

        <Col lg={9}>
          {loading && tickets.length === 0 ? (
            <Card>
              <Spinner message={t('common.loading')} />
            </Card>
          ) : paginatedTickets.length === 0 ? (
            <Card>
              <EmptyState
                icon="bi-inbox"
                title={t('tickets.noTickets') || 'No tickets found'}
                message={t('tickets.noTicketsMessage') || 'Try adjusting your filters'}
                actionLabel={activeFiltersCount > 0 ? t('tickets.clearFilters') : undefined}
                onAction={activeFiltersCount > 0 ? handleClearFilters : undefined}
              />
            </Card>
          ) : (
            <>
              {paginatedTickets.map((ticket) => (
                <TicketCard key={ticket.id} ticket={ticket} />
              ))}

              {paginationMetadata.totalPages > 1 && (
                <Card>
                  <Pagination
                    currentPage={currentPage}
                    totalPages={paginationMetadata.totalPages}
                    pageSize={pageSize}
                    onPageChange={handlePageChange}
                    onPageSizeChange={handlePageSizeChange}
                  />
                </Card>
              )}
            </>
          )}
        </Col>
      </Row>
    </ManagerLayout>
  );
};

export default TicketListPage;
