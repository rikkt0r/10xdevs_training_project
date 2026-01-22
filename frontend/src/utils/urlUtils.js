/**
 * Build query string from object
 * @param {object} params - Object with query parameters
 * @returns {string} Query string (without leading '?')
 */
export const buildQueryString = (params) => {
  if (!params || Object.keys(params).length === 0) {
    return '';
  }

  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      if (Array.isArray(value)) {
        value.forEach(item => searchParams.append(key, item));
      } else {
        searchParams.append(key, value);
      }
    }
  });

  return searchParams.toString();
};

/**
 * Parse query string to object
 * @param {string} queryString - Query string (with or without leading '?')
 * @returns {object} Object with parsed parameters
 */
export const parseQueryParams = (queryString) => {
  if (!queryString) return {};

  const cleanQuery = queryString.startsWith('?') ? queryString.slice(1) : queryString;
  const searchParams = new URLSearchParams(cleanQuery);
  const params = {};

  for (const [key, value] of searchParams.entries()) {
    if (params[key]) {
      if (Array.isArray(params[key])) {
        params[key].push(value);
      } else {
        params[key] = [params[key], value];
      }
    } else {
      params[key] = value;
    }
  }

  return params;
};

/**
 * Update URL query parameters without page reload
 * @param {object} params - New query parameters
 * @param {boolean} replace - Use replaceState instead of pushState
 */
export const updateQueryParams = (params, replace = false) => {
  const queryString = buildQueryString(params);
  const newUrl = queryString
    ? `${window.location.pathname}?${queryString}`
    : window.location.pathname;

  if (replace) {
    window.history.replaceState({}, '', newUrl);
  } else {
    window.history.pushState({}, '', newUrl);
  }
};

/**
 * Get current query parameters from URL
 * @returns {object} Current query parameters
 */
export const getCurrentQueryParams = () => {
  return parseQueryParams(window.location.search);
};

/**
 * Merge new params with existing query params
 * @param {object} newParams - New parameters to merge
 * @returns {object} Merged parameters
 */
export const mergeQueryParams = (newParams) => {
  const currentParams = getCurrentQueryParams();
  return { ...currentParams, ...newParams };
};

/**
 * Remove query parameters from URL
 * @param {string|string[]} keys - Parameter key(s) to remove
 */
export const removeQueryParams = (keys) => {
  const currentParams = getCurrentQueryParams();
  const keysToRemove = Array.isArray(keys) ? keys : [keys];

  keysToRemove.forEach(key => {
    delete currentParams[key];
  });

  updateQueryParams(currentParams, true);
};

/**
 * Build full URL with query parameters
 * @param {string} baseUrl - Base URL
 * @param {object} params - Query parameters
 * @returns {string} Full URL with query string
 */
export const buildUrl = (baseUrl, params) => {
  const queryString = buildQueryString(params);
  return queryString ? `${baseUrl}?${queryString}` : baseUrl;
};
