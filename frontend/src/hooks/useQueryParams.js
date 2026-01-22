import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';

/**
 * Custom hook for managing URL query parameters
 * Syncs state with URL query params
 */
const useQueryParams = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Get all query params as an object
  const queryParams = useMemo(() => {
    const params = {};
    for (const [key, value] of searchParams.entries()) {
      params[key] = value;
    }
    return params;
  }, [searchParams]);

  // Get a specific query param
  const getParam = useCallback((key, defaultValue = null) => {
    return searchParams.get(key) || defaultValue;
  }, [searchParams]);

  // Set a single query param
  const setParam = useCallback((key, value, replace = false) => {
    const newParams = new URLSearchParams(searchParams);

    if (value === null || value === undefined || value === '') {
      newParams.delete(key);
    } else {
      newParams.set(key, value);
    }

    setSearchParams(newParams, { replace });
  }, [searchParams, setSearchParams]);

  // Set multiple query params at once
  const setParams = useCallback((params, replace = false) => {
    const newParams = new URLSearchParams(searchParams);

    Object.entries(params).forEach(([key, value]) => {
      if (value === null || value === undefined || value === '') {
        newParams.delete(key);
      } else {
        newParams.set(key, value);
      }
    });

    setSearchParams(newParams, { replace });
  }, [searchParams, setSearchParams]);

  // Remove a query param
  const removeParam = useCallback((key, replace = false) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.delete(key);
    setSearchParams(newParams, { replace });
  }, [searchParams, setSearchParams]);

  // Remove multiple query params
  const removeParams = useCallback((keys, replace = false) => {
    const newParams = new URLSearchParams(searchParams);
    keys.forEach(key => newParams.delete(key));
    setSearchParams(newParams, { replace });
  }, [searchParams, setSearchParams]);

  // Clear all query params
  const clearParams = useCallback((replace = false) => {
    setSearchParams(new URLSearchParams(), { replace });
  }, [setSearchParams]);

  // Check if a param exists
  const hasParam = useCallback((key) => {
    return searchParams.has(key);
  }, [searchParams]);

  return {
    queryParams,
    getParam,
    setParam,
    setParams,
    removeParam,
    removeParams,
    clearParams,
    hasParam
  };
};

export default useQueryParams;
