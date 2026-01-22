# Component Library Documentation

Complete reference for all reusable components in the Simple Issue Tracker application.

## Table of Contents

1. [Common Components](#common-components)
2. [Layout Components](#layout-components)
3. [Feature Components](#feature-components)
4. [Hooks](#hooks)
5. [Utilities](#utilities)

---

## Common Components

### Button

Reusable button component with loading and disabled states.

**Props:**
- `children` (node) - Button content
- `variant` (string) - Button style: primary, secondary, danger, outline-*, etc. Default: 'primary'
- `size` (string) - Button size: sm, md, lg. Default: 'md'
- `type` (string) - Button type: button, submit, reset. Default: 'button'
- `disabled` (boolean) - Disable button. Default: false
- `loading` (boolean) - Show loading spinner. Default: false
- `fullWidth` (boolean) - Make button full width. Default: false
- `onClick` (function) - Click handler
- `className` (string) - Additional CSS classes

**Usage:**
```jsx
import Button from './components/common/Button';

<Button variant="primary" onClick={handleClick}>
  Click Me
</Button>

<Button variant="danger" loading disabled>
  Processing...
</Button>
```

**Accessibility:**
- Semantic `<button>` element
- `aria-busy` when loading
- Screen reader text for loading state
- Keyboard accessible
- Focus indicators

---

### Input

Form input component with validation and error handling.

**Props:**
- `type` (string) - Input type: text, email, password, number, etc. Default: 'text'
- `value` (string/number) - Input value
- `onChange` (function) - Change handler
- `onBlur` (function) - Blur handler
- `placeholder` (string) - Placeholder text
- `disabled` (boolean) - Disable input
- `readOnly` (boolean) - Make input read-only
- `error` (string) - Error message
- `className` (string) - Additional CSS classes

**Usage:**
```jsx
import Input from './components/common/Input';

<Input
  type="email"
  value={email}
  onChange={handleChange}
  error={errors.email}
  placeholder="Enter email"
/>
```

**Accessibility:**
- Associated with label via FormGroup
- `aria-invalid` when error present
- `aria-describedby` links to error message

---

### FormGroup

Wrapper for form inputs with label, error, and help text.

**Props:**
- `label` (string) - Field label (required)
- `htmlFor` (string) - ID of associated input (required)
- `error` (string) - Error message
- `helpText` (string) - Help text below input
- `required` (boolean) - Show required indicator
- `children` (node) - Input element

**Usage:**
```jsx
import FormGroup from './components/common/FormGroup';
import Input from './components/common/Input';

<FormGroup
  label="Email"
  htmlFor="email"
  error={errors.email}
  required
>
  <Input
    id="email"
    type="email"
    value={email}
    onChange={handleChange}
  />
</FormGroup>
```

---

### Modal

Accessible modal dialog with focus trap.

**Props:**
- `show` (boolean) - Show/hide modal (required)
- `onHide` (function) - Close handler (required)
- `title` (string) - Modal title
- `size` (string) - Modal size: sm, lg, xl
- `centered` (boolean) - Center vertically
- `children` (node) - Modal content

**Usage:**
```jsx
import Modal from './components/common/Modal';
import Button from './components/common/Button';

<Modal show={showModal} onHide={() => setShowModal(false)} title="Confirm Action">
  <p>Are you sure you want to proceed?</p>
  <div className="d-flex gap-2 justify-content-end">
    <Button variant="secondary" onClick={() => setShowModal(false)}>
      Cancel
    </Button>
    <Button variant="primary" onClick={handleConfirm}>
      Confirm
    </Button>
  </div>
</Modal>
```

**Accessibility:**
- Focus trap keeps focus within modal
- Closes on Escape key
- Returns focus to trigger element
- `aria-modal="true"` and `role="dialog"`
- Backdrop prevents background interaction

---

### Alert

Dismissible alert component for messages.

**Props:**
- `variant` (string) - Alert style: success, danger, warning, info
- `children` (node) - Alert content
- `dismissible` (boolean) - Show close button
- `onClose` (function) - Close handler
- `className` (string) - Additional CSS classes

**Usage:**
```jsx
import Alert from './components/common/Alert';

<Alert variant="success" dismissible onClose={() => setShowAlert(false)}>
  Profile updated successfully!
</Alert>

<Alert variant="danger">
  Failed to save changes. Please try again.
</Alert>
```

**Accessibility:**
- `role="alert"` for screen readers
- Keyboard-accessible close button

---

### Badge

Small status indicator component.

**Props:**
- `variant` (string) - Badge style: primary, success, danger, warning, info
- `children` (node) - Badge content
- `pill` (boolean) - Rounded pill shape
- `className` (string) - Additional CSS classes

**Usage:**
```jsx
import Badge from './components/common/Badge';

<Badge variant="success">Active</Badge>
<Badge variant="warning" pill>In Progress</Badge>
<Badge variant="danger">Closed</Badge>
```

---

### Card

Container component with optional header and footer.

**Props:**
- `title` (string) - Card title
- `header` (node) - Custom header content
- `footer` (node) - Footer content
- `children` (node) - Card body content
- `className` (string) - Additional CSS classes

**Usage:**
```jsx
import Card from './components/common/Card';

<Card title="Board Details">
  <p>Board information goes here...</p>
</Card>

<Card
  header={
    <div className="d-flex justify-content-between align-items-center">
      <h5>Custom Header</h5>
      <Button size="sm">Action</Button>
    </div>
  }
>
  Card content
</Card>
```

---

### Spinner

Loading indicator component.

**Props:**
- `size` (string) - Spinner size: sm, md, lg
- `variant` (string) - Color variant: primary, secondary, etc.
- `fullPage` (boolean) - Center in full page
- `message` (string) - Loading message
- `className` (string) - Additional CSS classes

**Usage:**
```jsx
import Spinner from './components/common/Spinner';

<Spinner size="lg" message="Loading..." />
<Spinner fullPage message="Please wait..." />
```

**Accessibility:**
- `role="status"` for screen readers
- `aria-live="polite"` for status updates

---

### EmptyState

Placeholder for empty lists or data.

**Props:**
- `icon` (string) - Bootstrap icon class (e.g., 'bi-inbox')
- `title` (string) - Empty state title
- `message` (string) - Description message
- `actionLabel` (string) - Call-to-action button text
- `onAction` (function) - Button click handler
- `className` (string) - Additional CSS classes

**Usage:**
```jsx
import EmptyState from './components/common/EmptyState';

<EmptyState
  icon="bi-inbox"
  title="No inboxes configured"
  message="Add an email inbox to start receiving tickets"
  actionLabel="Add Inbox"
  onAction={() => navigate('/settings/inboxes/new')}
/>
```

---

### Skeleton

Loading placeholder components.

**Components:**
- `Skeleton` - Base skeleton element
- `SkeletonText` - Text lines
- `SkeletonCard` - Card skeleton
- `SkeletonTable` - Table skeleton
- `SkeletonList` - List items
- `SkeletonForm` - Form fields

**Usage:**
```jsx
import Skeleton, { SkeletonCard, SkeletonText } from './components/common/Skeleton';

{loading ? (
  <SkeletonCard />
) : (
  <Card>{content}</Card>
)}

<SkeletonText lines={3} />
```

---

### ErrorBoundary

Error boundary component with multiple levels.

**Props:**
- `level` (string) - Error level: app, route, widget. Default: 'route'
- `fallback` (node/function) - Custom error UI
- `onError` (function) - Error callback
- `onReset` (function) - Reset callback
- `widgetName` (string) - Widget name for widget-level errors
- `children` (node) - Protected components

**Usage:**
```jsx
import ErrorBoundary from './components/common/ErrorBoundary';

// App-level (wrap entire app)
<ErrorBoundary level="app">
  <App />
</ErrorBoundary>

// Route-level (wrap page content)
<ErrorBoundary level="route">
  <BoardDetailPage />
</ErrorBoundary>

// Widget-level (wrap component)
<ErrorBoundary level="widget" widgetName="Board Stats">
  <BoardStats />
</ErrorBoundary>
```

**Features:**
- Different UIs for each level
- Development error details
- Reset functionality
- Custom fallback support

---

## Layout Components

### ManagerLayout

Main layout for authenticated manager pages.

**Props:**
- `children` (node) - Page content
- `breadcrumbs` (array) - Breadcrumb items

**Usage:**
```jsx
import ManagerLayout from './components/layout/ManagerLayout';

const breadcrumbs = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'Boards', path: '/boards' },
  { label: 'Support' }
];

<ManagerLayout breadcrumbs={breadcrumbs}>
  <h1>Board Details</h1>
  {/* Page content */}
</ManagerLayout>
```

**Features:**
- Sidebar navigation
- Header with user menu
- Breadcrumbs
- Skip-to-content link
- Responsive (collapsible sidebar on mobile)

---

### PublicLayout

Layout for public-facing pages (ticket forms, view).

**Props:**
- `children` (node) - Page content

**Usage:**
```jsx
import PublicLayout from './components/layout/PublicLayout';

<PublicLayout>
  <PublicTicketFormPage />
</PublicLayout>
```

---

## Hooks

### useFormValidation

Form state and validation management.

**Parameters:**
- `initialValues` (object) - Initial form values
- `validationRules` (object) - Validation functions per field

**Returns:**
- `values` (object) - Current form values
- `errors` (object) - Validation errors
- `touched` (object) - Touched fields
- `handleChange` (function) - Change handler
- `handleBlur` (function) - Blur handler
- `handleSubmit` (function) - Submit wrapper
- `setFieldValue` (function) - Set specific field
- `resetForm` (function) - Reset to initial values

**Usage:**
```jsx
import useFormValidation from './hooks/useFormValidation';
import { validateRequired, validateEmail } from './utils/validationUtils';

const validationRules = {
  email: (value) => validateEmail(value, 'Invalid email'),
  password: (value) => validateRequired(value, 'Password required'),
};

const { values, errors, touched, handleChange, handleBlur, handleSubmit } =
  useFormValidation({ email: '', password: '' }, validationRules);

const onSubmit = async (formValues) => {
  await api.login(formValues);
};

<form onSubmit={handleSubmit(onSubmit)}>
  <input
    name="email"
    value={values.email}
    onChange={handleChange}
    onBlur={handleBlur}
  />
  {touched.email && errors.email && <div>{errors.email}</div>}
</form>
```

---

### usePagination

Pagination state management.

**Parameters:**
- `totalItems` (number) - Total number of items
- `itemsPerPage` (number) - Items per page (default: 10)

**Returns:**
- `currentPage` (number)
- `totalPages` (number)
- `startIndex` (number)
- `endIndex` (number)
- `goToPage` (function)
- `nextPage` (function)
- `prevPage` (function)
- `canGoNext` (boolean)
- `canGoPrev` (boolean)

**Usage:**
```jsx
import usePagination from './hooks/usePagination';

const { currentPage, totalPages, startIndex, endIndex, goToPage, nextPage, prevPage } =
  usePagination(items.length, 10);

const currentItems = items.slice(startIndex, endIndex);

<Pagination
  currentPage={currentPage}
  totalPages={totalPages}
  onPageChange={goToPage}
/>
```

---

### useDebounce

Debounce value changes.

**Parameters:**
- `value` (any) - Value to debounce
- `delay` (number) - Delay in ms (default: 500)

**Returns:**
- Debounced value

**Usage:**
```jsx
import useDebounce from './hooks/useDebounce';

const [searchTerm, setSearchTerm] = useState('');
const debouncedSearch = useDebounce(searchTerm, 500);

useEffect(() => {
  if (debouncedSearch) {
    searchAPI(debouncedSearch);
  }
}, [debouncedSearch]);

<input
  value={searchTerm}
  onChange={(e) => setSearchTerm(e.target.value)}
  placeholder="Search..."
/>
```

---

### useQueryParams

URL query parameter management.

**Returns:**
- `queryParams` (object) - All query params
- `getParam` (function) - Get single param
- `setParam` (function) - Set single param
- `setParams` (function) - Set multiple params
- `removeParam` (function) - Remove param
- `clearParams` (function) - Clear all params
- `hasParam` (function) - Check if param exists

**Usage:**
```jsx
import useQueryParams from './hooks/useQueryParams';

const { getParam, setParam } = useQueryParams();

const page = getParam('page', '1');
const filter = getParam('filter');

<button onClick={() => setParam('page', '2')}>Next Page</button>
<button onClick={() => setParam('filter', 'active')}>Show Active</button>
```

---

### useToast

Toast notification system.

**Returns:**
- `showToast` (function) - Show generic toast
- `success` (function) - Show success toast
- `error` (function) - Show error toast
- `warning` (function) - Show warning toast
- `info` (function) - Show info toast

**Usage:**
```jsx
import { useToast } from './contexts/ToastContext';

const toast = useToast();

// Success
toast.success('Profile updated successfully!');

// Error
toast.error('Failed to save changes');

// Custom
toast.showToast('Custom message', {
  variant: 'warning',
  title: 'Warning',
  autoHide: false,
});
```

---

## Utilities

### Validation Utils (`utils/validationUtils.js`)

- `validateRequired(value, message)` - Check if value exists
- `validateEmail(value, message)` - Validate email format
- `validatePassword(value, message)` - Check password strength (min 8 chars)
- `validatePasswordConfirmation(password, confirmation, message)` - Match passwords
- `validatePort(value, message)` - Validate port number (1-65535)

### Date Utils (`utils/dateUtils.js`)

- `formatDate(date, format)` - Format date with date-fns
- `formatRelativeDate(date)` - Relative time (e.g., "2 hours ago")
- `formatDateTime(date)` - Full date and time
- `parseDate(dateString)` - Parse ISO date string

### Timezone Utils (`utils/timezoneUtils.js`)

- `getTimezones()` - List of common IANA timezones
- `getBrowserTimezone()` - Detect browser timezone
- `formatInTimezone(date, timezone, options)` - Format date in specific timezone

### Accessibility Utils (`utils/accessibilityUtils.js`)

- `generateId(prefix)` - Generate unique ID for form elements
- `announceToScreenReader(message, priority)` - ARIA live region announcement
- `createFocusTrap(containerElement)` - Focus trap for modals
- `handleKeyboardClick(event, callback)` - Handle Enter/Space as click
- `prefersReducedMotion()` - Check reduced motion preference

---

## Styling

### Global Styles
- `App.css` - Global app styles, accessibility utilities
- `styles/responsive.css` - Responsive utilities and breakpoints

### CSS Classes

**Accessibility:**
- `.sr-only` - Screen reader only
- `.skip-to-content` - Skip link

**Responsive:**
- `.mobile-only` - Show on mobile only
- `.tablet-up` - Show on tablet+
- `.desktop-up` - Show on desktop+
- `.stack-mobile` - Vertical on mobile, horizontal on tablet+

**Layout:**
- `.grid-responsive` - 1/2/3 column grid
- `.form-row-responsive` - Responsive form row

---

## Best Practices

1. **Always use FormGroup with Input** for proper labeling
2. **Use semantic HTML** (`<button>`, `<nav>`, `<main>`)
3. **Provide aria-labels** for icon-only buttons
4. **Test keyboard navigation** for all interactive elements
5. **Use ErrorBoundary** to catch component errors
6. **Implement loading states** with Skeleton components
7. **Show user feedback** with Toast notifications
8. **Validate forms** client-side before submission
9. **Handle errors gracefully** with specific messages
10. **Keep components accessible** following WCAG 2.1 AA

---

Last Updated: 2026-01-22
