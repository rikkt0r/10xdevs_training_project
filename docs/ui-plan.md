# UI Architecture Plan

## Tech Stack
- React (JS), Redux Toolkit + RTK Query, Bootstrap, react-i18next, React Router v6

## Route Structure

| Route | Auth | Description |
|-------|------|-------------|
| `/login` | Public | Login form |
| `/register` | Public | Registration form |
| `/verify-email` | Public | Email verification page |
| `/forgot-password` | Public | Password reset request |
| `/reset-password` | Public | Password reset form |
| `/dashboard` | JWT | Main dashboard |
| `/boards` | JWT | Board list |
| `/boards/:id` | JWT | Board detail + ticket list |
| `/boards/:id/tickets/:ticketId` | JWT | Ticket detail |
| `/standby-queue` | JWT | Standby queue list |
| `/standby-queue/:id` | JWT | Queue item detail |
| `/settings/profile` | JWT | Profile settings |
| `/settings/security` | JWT | Password change |
| `/settings/inboxes` | JWT | Email inbox management |
| `/settings/inboxes/:id` | JWT | Inbox configuration |
| `/board/:uniqueName` | Public | Public ticket form |
| `/ticket/:uuid` | Public | Public ticket view |

## Layout Components

```
ManagerLayout (authenticated)
├── Sidebar (Dashboard, Boards, Standby Queue, Settings)
├── Header (language switcher, user menu)
└── Main content + Breadcrumbs

PublicLayout (unauthenticated)
├── Minimal header
└── Centered content
```

## State Management

**Redux Slices:**
- `auth` - JWT tokens (memory only), user profile, timezone
- RTK Query API slices for all endpoints

**Cache Strategy:**
- 30s cache lifetime, stale-while-revalidate
- Tag-based invalidation on mutations
- 60s polling for dashboard stats

## Component Library (`src/components/common/`)

| Component | Variants/Notes |
|-----------|----------------|
| Button | primary, secondary, danger |
| Card | header, body, footer slots |
| Modal | standard, danger confirmation |
| Input/Select/Textarea | with validation states |
| Badge | state colors (new=blue, in_progress=yellow, closed=green, rejected=red) |
| Alert | success, error, warning, info |
| Spinner | inline, full-page |
| Pagination | numbered, page size selector |
| EmptyState | icon, text, CTA |
| Toast | via ToastContext, top-right, max 3 |
| Timeline | for status history |

## Key UI Patterns

### Authentication
- JWT in memory (not localStorage)
- Axios interceptor for 401 → auto-refresh → retry
- On refresh failure → clear auth → redirect to login

### Forms
- React Hook Form for validation
- Inline error display per field
- Two-step for inbox config: test connection → save

### Filters & Pagination
- URL query params for all filters (`?state=new&page=2&sort=created_at`)
- Persist page size in localStorage
- Collapsible filter panel with active count badge

### Confirmations
- Danger modal for destructive actions
- Multi-step wizard for account suspension

### Loading States
- Skeleton loaders for initial load
- Inline spinners for actions
- Progress indicator for long operations (inbox test)

### Empty States
- Contextual message + illustration + CTA
- Never generic "No data"

### Error Handling
- Error boundaries: App > Route > Widget level
- Toast for async errors
- Inline for form validation

## i18n

- Languages: EN (default), PL
- Detection: localStorage → browser → EN
- JSON files in `src/locales/{lang}.json`
- API calls include `Accept-Language` header

## Accessibility (WCAG 2.1 AA)

- Semantic HTML, proper heading hierarchy
- Visible focus indicators
- aria-labels for icon-only buttons
- Color + text for state indicators
- 44x44px minimum touch targets
- Skip-to-content link

## Responsive Breakpoints

| Breakpoint | Layout |
|------------|--------|
| <768px | Stacked widgets, collapsible sidebar, accordion lists |
| 768-1024px | 2-column grid, persistent sidebar |
| >1024px | 3-column grid, full sidebar |

## View Specifications

### Dashboard
- Board list with ticket counts + quick actions
- Standby queue count badge/alert
- Recent tickets feed (10 items)

### Board Detail
- Board info header (name, greeting, external platform indicator)
- Ticket table with filters (state, date, search)
- Pagination controls
- State change via dropdown in table rows

### Ticket Detail
- Full ticket content (title, description, creator email, source)
- State change buttons (valid transitions only)
- Comment input for state change
- Status change timeline

### Standby Queue Item
- Email preview (subject, body, sender)
- "Assign to Board" dropdown + confirm
- "Retry External" button (if applicable)
- "Discard" with confirmation

### Public Ticket Form
- Greeting message from board
- Fields: email, title, description
- Inline validation
- Success message with "check your email" note
- Error states: 404, 410 (archived), 403 (suspended with message)

### Public Ticket View
- Ticket info (title, description, state, board name)
- Status timeline with manager comments
- For external tickets: redirect info to external URL
