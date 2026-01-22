import { useState, useCallback, useMemo } from 'react';

/**
 * Custom hook for pagination state management
 * Manages page number, page size, and provides utility methods
 */
const usePagination = (initialPage = 1, initialPageSize = 10) => {
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);

  const handlePageChange = useCallback((page) => {
    setCurrentPage(page);
  }, []);

  const handlePageSizeChange = useCallback((newSize) => {
    setPageSize(newSize);
    setCurrentPage(1); // Reset to first page when page size changes
  }, []);

  const nextPage = useCallback(() => {
    setCurrentPage(prev => prev + 1);
  }, []);

  const prevPage = useCallback(() => {
    setCurrentPage(prev => Math.max(1, prev - 1));
  }, []);

  const goToFirstPage = useCallback(() => {
    setCurrentPage(1);
  }, []);

  const goToLastPage = useCallback((totalPages) => {
    setCurrentPage(totalPages);
  }, []);

  const reset = useCallback(() => {
    setCurrentPage(initialPage);
    setPageSize(initialPageSize);
  }, [initialPage, initialPageSize]);

  // Calculate pagination metadata
  const getPaginationMetadata = useCallback((totalItems) => {
    const totalPages = Math.ceil(totalItems / pageSize);
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = Math.min(startIndex + pageSize, totalItems);

    return {
      currentPage,
      pageSize,
      totalPages,
      totalItems,
      startIndex,
      endIndex,
      hasNextPage: currentPage < totalPages,
      hasPrevPage: currentPage > 1
    };
  }, [currentPage, pageSize]);

  // Get paginated slice of data
  const getPaginatedData = useCallback((data = []) => {
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return data.slice(startIndex, endIndex);
  }, [currentPage, pageSize]);

  return {
    currentPage,
    pageSize,
    handlePageChange,
    handlePageSizeChange,
    nextPage,
    prevPage,
    goToFirstPage,
    goToLastPage,
    reset,
    getPaginationMetadata,
    getPaginatedData
  };
};

export default usePagination;
