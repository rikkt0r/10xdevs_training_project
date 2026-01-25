# Dashboard Page Tests

## Overview

Comprehensive test suite for the DashboardPage component covering:
- Loading states
- Error handling
- Statistics display
- Recent tickets
- Quick actions
- Accessibility

## Test Structure

The test suite is organized into logical groups:

### Loading State
- Verifies loading spinner displays while fetching data
- Confirms API services are called correctly on mount

### Error State
- Tests error message display when API fails
- Tests fallback error message handling

### Statistics Cards
- Validates all dashboard statistics are displayed correctly
- Tests board counts, ticket counts by state

### Tickets By State Section
- Verifies ticket state breakdown display
- Tests state labels and badges

### Recent Activity Section
- Tests daily and weekly ticket creation stats

### Quick Actions Section
- Validates action button links
- Tests conditional rendering (standby queue button)

### Recent Tickets Section
- Tests ticket list display
- Validates ticket metadata (boards, states, dates)
- Tests ticket navigation links

### Empty State
- Tests no tickets display

### Accessibility
- Validates heading hierarchy
- Tests keyboard accessibility

### Data Refresh
- Ensures data is only fetched once on mount

### Integration
- Full end-to-end dashboard rendering test

## Running Tests

```bash
# Run dashboard tests only
npm test -- --testPathPattern=DashboardPage

# Run with coverage
npm test -- --testPathPattern=DashboardPage --coverage

# Run in watch mode
npm test -- --testPathPattern=DashboardPage --watch
```

## Mock Data

The test suite uses realistic mock data for:
- Dashboard statistics (boards, tickets, queues)
- Recent tickets with full metadata
- Error responses

## Test Utilities

A comprehensive set of test utilities is available in `src/utils/testUtils.js`:

- `renderWithRouter()` - Render with Router wrapper
- `renderWithProviders()` - Render with Redux + Router
- `create Mock*()` - Factory functions for mock data
- Mock formatters and helpers

## Notes

### Service Layer Updates Required

The tests exposed that the `dashboardService.js` needed to be updated to properly unwrap DataResponse wrappers from the API, matching the pattern used in other services:

```javascript
// Before
export const getDashboardStats = () => {
  return api.get('/dashboard/stats');
};

// After
export const getDashboardStats = async () => {
  const response = await api.get('/dashboard/stats');
  return response.data.data; // Extract data from DataResponse wrapper
};
```

### Component Updates

The `DashboardPage.js` component was updated to work with the corrected service layer:

```javascript
// Before
const [statsResponse, ticketsResponse] = await Promise.all([...]);
setStats(statsResponse.data.data);

// After
const [stats, tickets] = await Promise.all([...]);
setStats(stats);
```

## Test Coverage

The test suite provides comprehensive coverage of:
- ✅ Component rendering in all states
- ✅ API integration
- ✅ Error handling
- ✅ User interactions (navigation links)
- ✅ Conditional rendering
- ✅ Accessibility features
- ✅ Data fetching lifecycle

## Future Improvements

1. Add integration tests with real Redux store
2. Add tests for real-time updates
3. Test responsive behavior
4. Add performance tests for large datasets
5. Test internationalization (i18n) thoroughly
6. Add visual regression tests

## Debugging

If tests fail, check:

1. **Mocks are properly configured** - Ensure all services, utilities, and dependencies are mocked
2. **Async operations complete** - Use `waitFor()` for async state changes
3. **Data format matches** - Verify mock data structure matches component expectations
4. **Router context** - Ensure components are wrapped with `BrowserRouter`

## Related Files

- Component: `src/pages/DashboardPage.js`
- Services: `src/services/dashboardService.js`
- Test Utilities: `src/utils/testUtils.js`
- Component Tests: `src/pages/__tests__/DashboardPage.test.js`
