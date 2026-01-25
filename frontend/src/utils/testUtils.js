/**
 * Test utilities for frontend testing
 * Provides common mocks and helper functions for tests
 */

import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

/**
 * Render component with Router wrapper
 */
export const renderWithRouter = (component, { route = '/' } = {}) => {
  window.history.pushState({}, 'Test page', route);
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

/**
 * Render component with Redux store and Router
 */
export const renderWithProviders = (
  component,
  {
    preloadedState = {},
    store = configureStore({ reducer: {}, preloadedState }),
    route = '/',
    ...renderOptions
  } = {}
) => {
  window.history.pushState({}, 'Test page', route);

  function Wrapper({ children }) {
    return (
      <Provider store={store}>
        <BrowserRouter>{children}</BrowserRouter>
      </Provider>
    );
  }

  return {
    store,
    ...render(component, { wrapper: Wrapper, ...renderOptions }),
  };
};

/**
 * Create mock translation function for i18next
 */
export const mockTranslation = (customTranslations = {}) => {
  return {
    t: (key) => customTranslations[key] || key,
    i18n: {
      language: 'en',
      changeLanguage: jest.fn(),
    },
  };
};

/**
 * Create mock API response wrapper (DataResponse format)
 */
export const createMockDataResponse = (data) => ({
  data: { data },
});

/**
 * Create mock paginated API response
 */
export const createMockPaginatedResponse = (data, pagination = {}) => ({
  data: {
    data,
    pagination: {
      page: 1,
      limit: 10,
      total_items: data.length,
      total_pages: 1,
      ...pagination,
    },
  },
});

/**
 * Create mock error response
 */
export const createMockErrorResponse = (message = 'Error occurred') => ({
  response: {
    data: {
      error: { message },
    },
  },
});

/**
 * Mock dashboard stats data
 */
export const createMockDashboardStats = (overrides = {}) => ({
  boards_count: 5,
  active_boards_count: 4,
  standby_queue_count: 3,
  tickets_by_state: {
    new: 10,
    in_progress: 7,
    waiting: 2,
    closed: 25,
    rejected: 1,
  },
  recent_activity: {
    tickets_created_today: 5,
    tickets_created_this_week: 15,
  },
  ...overrides,
});

/**
 * Create mock ticket data
 */
export const createMockTicket = (overrides = {}) => ({
  id: 1,
  uuid: 'test-uuid',
  title: 'Test Ticket',
  description: 'Test description',
  state: 'new',
  created_at: '2026-01-25T10:00:00Z',
  updated_at: '2026-01-25T10:00:00Z',
  board: {
    id: 1,
    name: 'Test Board',
  },
  ...overrides,
});

/**
 * Create mock board data
 */
export const createMockBoard = (overrides = {}) => ({
  id: 1,
  name: 'Test Board',
  unique_name: 'test-board',
  greeting: 'Welcome!',
  archived: false,
  external_platform: null,
  ticket_counts: {
    new: 5,
    in_progress: 3,
    waiting: 1,
    resolved: 10,
  },
  created_at: '2026-01-25T10:00:00Z',
  updated_at: '2026-01-25T10:00:00Z',
  ...overrides,
});

/**
 * Create mock manager profile data
 */
export const createMockManager = (overrides = {}) => ({
  id: 1,
  email: 'test@example.com',
  name: 'Test Manager',
  timezone: 'UTC',
  created_at: '2026-01-25T10:00:00Z',
  ...overrides,
});

/**
 * Wait for async operations to complete
 */
export const waitForAsync = () =>
  new Promise((resolve) => setTimeout(resolve, 0));

/**
 * Mock localStorage
 */
export const createMockLocalStorage = () => {
  let store = {};

  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString();
    },
    removeItem: (key) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
};

/**
 * Setup mock date for consistent testing
 */
export const mockDate = (dateString = '2026-01-25T12:00:00Z') => {
  const mockDate = new Date(dateString);
  const realDateNow = Date.now.bind(global.Date);

  beforeAll(() => {
    global.Date.now = jest.fn(() => mockDate.getTime());
  });

  afterAll(() => {
    global.Date.now = realDateNow;
  });

  return mockDate;
};

/**
 * Mock common utility functions
 */
export const mockUtilityFunctions = () => {
  jest.mock('../utils/dateUtils', () => ({
    formatRelativeDate: jest.fn((date) => '2 hours ago'),
    formatDate: jest.fn((date) => 'Jan 25, 2026'),
    formatDateTime: jest.fn((date) => 'Jan 25, 2026, 12:00 PM'),
  }));

  jest.mock('../utils/ticketUtils', () => ({
    getStateBadgeVariant: jest.fn((state) => {
      const variants = {
        new: 'primary',
        in_progress: 'info',
        waiting: 'warning',
        resolved: 'success',
        closed: 'secondary',
        rejected: 'danger',
      };
      return variants[state] || 'secondary';
    }),
    getStateLabel: jest.fn((state) => {
      const labels = {
        new: 'New',
        in_progress: 'In Progress',
        waiting: 'Waiting',
        resolved: 'Resolved',
        closed: 'Closed',
        rejected: 'Rejected',
      };
      return labels[state] || state;
    }),
  }));
};
