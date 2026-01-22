import React from 'react';
import { Pagination as BootstrapPagination, Form } from 'react-bootstrap';

/**
 * Reusable Pagination component
 * Numbered pagination with page size selector
 */
const Pagination = ({
  currentPage = 1,
  totalPages = 1,
  onPageChange,
  pageSize = 10,
  pageSizeOptions = [10, 25, 50, 100],
  onPageSizeChange,
  showPageSize = true,
  className = '',
}) => {
  const maxVisiblePages = 5;

  const getPageNumbers = () => {
    const pages = [];
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage < maxVisiblePages - 1) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return pages;
  };

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
      onPageChange(page);
    }
  };

  const handlePageSizeChange = (e) => {
    const newSize = parseInt(e.target.value, 10);
    onPageSizeChange(newSize);
  };

  if (totalPages <= 1 && !showPageSize) {
    return null;
  }

  return (
    <div className={`d-flex justify-content-between align-items-center ${className}`}>
      <div>
        {showPageSize && onPageSizeChange && (
          <div className="d-flex align-items-center">
            <Form.Label className="mb-0 me-2">Items per page:</Form.Label>
            <Form.Select
              value={pageSize}
              onChange={handlePageSizeChange}
              style={{ width: 'auto' }}
              size="sm"
            >
              {pageSizeOptions.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </Form.Select>
          </div>
        )}
      </div>

      {totalPages > 1 && (
        <BootstrapPagination className="mb-0">
          <BootstrapPagination.First
            onClick={() => handlePageChange(1)}
            disabled={currentPage === 1}
          />
          <BootstrapPagination.Prev
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
          />

          {getPageNumbers()[0] > 1 && (
            <>
              <BootstrapPagination.Item onClick={() => handlePageChange(1)}>
                1
              </BootstrapPagination.Item>
              {getPageNumbers()[0] > 2 && <BootstrapPagination.Ellipsis disabled />}
            </>
          )}

          {getPageNumbers().map(page => (
            <BootstrapPagination.Item
              key={page}
              active={page === currentPage}
              onClick={() => handlePageChange(page)}
            >
              {page}
            </BootstrapPagination.Item>
          ))}

          {getPageNumbers()[getPageNumbers().length - 1] < totalPages && (
            <>
              {getPageNumbers()[getPageNumbers().length - 1] < totalPages - 1 && (
                <BootstrapPagination.Ellipsis disabled />
              )}
              <BootstrapPagination.Item onClick={() => handlePageChange(totalPages)}>
                {totalPages}
              </BootstrapPagination.Item>
            </>
          )}

          <BootstrapPagination.Next
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          />
          <BootstrapPagination.Last
            onClick={() => handlePageChange(totalPages)}
            disabled={currentPage === totalPages}
          />
        </BootstrapPagination>
      )}
    </div>
  );
};

export default Pagination;
