# Testing Guide

This document outlines the testing strategy and best practices for the Simple Issue Tracker frontend application.

## Testing Stack

- **Test Runner**: Jest (via react-scripts)
- **Testing Library**: @testing-library/react
- **User Interaction**: @testing-library/user-event
- **Assertions**: @testing-library/jest-dom

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test Button.test.js

# Run tests matching pattern
npm test -- --testNamePattern="renders"
```

## Test Organization

```
src/
├── components/
│   └── common/
│       ├── Button.js
│       └── __tests__/
│           └── Button.test.js
├── pages/
│   └── __tests__/
│       └── LoginPage.test.js
├── hooks/
│   └── __tests__/
│       └── useFormValidation.test.js
└── utils/
    └── __tests__/
        └── validationUtils.test.js
```

## Testing Principles

### 1. Test User Behavior, Not Implementation

Focus on what users see and do, not internal component state.

**❌ Bad**:
```javascript
expect(wrapper.state('count')).toBe(5);
```

**✅ Good**:
```javascript
expect(screen.getByText('Count: 5')).toBeInTheDocument();
```

### 2. Use Accessible Queries

Prioritize queries that reflect how users interact with your app.

**Query Priority** (most → least preferred):
1. `getByRole` - Best for accessibility
2. `getByLabelText` - For form inputs
3. `getByPlaceholderText` - For inputs without labels
4. `getByText` - For non-interactive elements
5. `getByTestId` - Last resort

**❌ Bad**:
```javascript
container.querySelector('.button-class');
```

**✅ Good**:
```javascript
screen.getByRole('button', { name: 'Submit' });
```

### 3. Test Accessibility

Ensure components are accessible in tests.

```javascript
it('is keyboard accessible', () => {
  render(<Button onClick={handleClick}>Click me</Button>);
  const button = screen.getByRole('button');
  button.focus();
  expect(button).toHaveFocus();
});

it('has correct ARIA attributes', () => {
  render(<Button loading>Submit</Button>);
  expect(screen.getByRole('button')).toHaveAttribute('aria-busy', 'true');
});
```

## Component Testing Patterns

### Testing Rendering

```javascript
describe('Button Component', () => {
  it('renders with children text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('applies variant styles', () => {
    const { container } = render(<Button variant="primary">Button</Button>);
    expect(container.firstChild).toHaveClass('btn-primary');
  });
});
```

### Testing User Interaction

```javascript
describe('User Interactions', () => {
  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick} disabled>Click me</Button>);

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).not.toHaveBeenCalled();
  });
});
```

### Testing Forms

```javascript
import userEvent from '@testing-library/user-event';

describe('LoginForm', () => {
  it('submits form with correct values', async () => {
    const user = userEvent.setup();
    const handleSubmit = jest.fn();

    render(<LoginForm onSubmit={handleSubmit} />);

    await user.type(screen.getByLabelText('Email'), 'user@example.com');
    await user.type(screen.getByLabelText('Password'), 'password123');
    await user.click(screen.getByRole('button', { name: 'Login' }));

    expect(handleSubmit).toHaveBeenCalledWith({
      email: 'user@example.com',
      password: 'password123',
    });
  });

  it('shows validation errors', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    await user.click(screen.getByRole('button', { name: 'Login' }));

    expect(screen.getByText('Email is required')).toBeInTheDocument();
  });
});
```

### Testing Async Operations

```javascript
import { waitFor } from '@testing-library/react';

describe('DataFetching', () => {
  it('shows loading state then data', async () => {
    render(<UserList />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('shows error message on failure', async () => {
    // Mock API to return error
    jest.spyOn(api, 'getUsers').mockRejectedValue(new Error('Failed to fetch'));

    render(<UserList />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load users')).toBeInTheDocument();
    });
  });
});
```

### Testing Redux-Connected Components

```javascript
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../store/slices/authSlice';

const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      auth: authReducer,
    },
    preloadedState: initialState,
  });
};

describe('LoginPage', () => {
  it('dispatches login action on submit', async () => {
    const store = createMockStore();
    const user = userEvent.setup();

    render(
      <Provider store={store}>
        <LoginPage />
      </Provider>
    );

    await user.type(screen.getByLabelText('Email'), 'user@example.com');
    await user.type(screen.getByLabelText('Password'), 'password123');
    await user.click(screen.getByRole('button', { name: 'Login' }));

    // Check store state or spyOn dispatch
    const actions = store.getState();
    expect(actions.auth.loading).toBe(true);
  });
});
```

### Testing Modals

```javascript
describe('ConfirmModal', () => {
  it('calls onConfirm when confirmed', async () => {
    const user = userEvent.setup();
    const handleConfirm = jest.fn();

    render(
      <ConfirmModal
        show={true}
        onConfirm={handleConfirm}
        title="Delete Item"
        message="Are you sure?"
      />
    );

    await user.click(screen.getByRole('button', { name: 'Confirm' }));
    expect(handleConfirm).toHaveBeenCalled();
  });

  it('traps focus within modal', () => {
    render(<ConfirmModal show={true} title="Modal" message="Message" />);

    const modal = screen.getByRole('dialog');
    const buttons = within(modal).getAllByRole('button');

    expect(document.activeElement).toBe(buttons[0]); // First button focused
  });
});
```

## Mocking

### Mocking API Calls

```javascript
import * as api from '../services/api';

describe('API Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches and displays data', async () => {
    jest.spyOn(api, 'getBoards').mockResolvedValue({
      data: [{ id: 1, name: 'Support' }],
    });

    render(<BoardList />);

    await waitFor(() => {
      expect(screen.getByText('Support')).toBeInTheDocument();
    });
  });
});
```

### Mocking React Router

```javascript
import { MemoryRouter } from 'react-router-dom';

describe('Navigation', () => {
  it('navigates to detail page on click', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={['/boards']}>
        <BoardList />
      </MemoryRouter>
    );

    await user.click(screen.getByText('View Board'));

    expect(window.location.pathname).toBe('/boards/1');
  });
});
```

### Mocking Hooks

```javascript
import * as hooks from '../hooks/useFormValidation';

describe('FormComponent', () => {
  it('handles validation errors', () => {
    jest.spyOn(hooks, 'useFormValidation').mockReturnValue({
      values: {},
      errors: { email: 'Invalid email' },
      touched: { email: true },
      handleChange: jest.fn(),
      handleBlur: jest.fn(),
      handleSubmit: jest.fn(),
    });

    render(<LoginForm />);

    expect(screen.getByText('Invalid email')).toBeInTheDocument();
  });
});
```

## Integration Testing

Test complete user flows across multiple components.

```javascript
describe('Ticket Creation Flow', () => {
  it('allows user to create a ticket from board detail page', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={['/boards/1']}>
        <Provider store={store}>
          <App />
        </Provider>
      </MemoryRouter>
    );

    // Navigate to create ticket
    await user.click(screen.getByRole('button', { name: 'New Ticket' }));

    // Fill form
    await user.type(screen.getByLabelText('Title'), 'Bug in login');
    await user.type(screen.getByLabelText('Description'), 'Cannot log in');

    // Submit
    await user.click(screen.getByRole('button', { name: 'Create' }));

    // Verify success
    await waitFor(() => {
      expect(screen.getByText('Ticket created successfully')).toBeInTheDocument();
    });
  });
});
```

## Coverage Goals

- **Overall**: 80% minimum
- **Common Components**: 90%+ (Button, Input, Modal, etc.)
- **Critical Flows**: 100% (Auth, ticket creation, board management)
- **Utilities**: 95%+ (validation, formatting, etc.)

```bash
npm test -- --coverage --watchAll=false
```

## Best Practices

### ✅ Do
- Test user-visible behavior
- Use accessible queries
- Test error states
- Test loading states
- Test keyboard interactions
- Mock external dependencies
- Write descriptive test names
- Group related tests with `describe`
- Use `beforeEach` for common setup
- Test edge cases

### ❌ Don't
- Test implementation details
- Use `container.querySelector`
- Test third-party libraries
- Duplicate tests
- Test inline styles
- Over-mock (mock only what's necessary)
- Write tests that depend on each other
- Skip cleanup
- Use `act()` manually (RTL handles it)

## Continuous Integration

Tests run automatically on:
- Every commit (pre-commit hook)
- Pull requests
- Main branch pushes

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm test -- --coverage --watchAll=false
```

## Resources

- [Testing Library Docs](https://testing-library.com/docs/react-testing-library/intro/)
- [Jest Docs](https://jestjs.io/docs/getting-started)
- [Common Testing Mistakes](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [React Testing Best Practices](https://testingjavascript.com/)

## Example Test Checklist

For each component, test:
- [ ] Renders correctly with default props
- [ ] Renders with all prop variants
- [ ] Handles user interactions (click, type, etc.)
- [ ] Shows loading states
- [ ] Shows error states
- [ ] Accessibility (keyboard, screen readers)
- [ ] Edge cases (empty data, long text, etc.)
- [ ] Integration with parent components

Last Updated: 2026-01-22
