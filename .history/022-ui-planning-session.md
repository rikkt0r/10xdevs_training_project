# UI Planning Session - Questions & Recommendations

**Date:** 2026-01-22
**Status:** Completed
**Output:** docs/ui-plan.md

---

## Session Summary

This session analyzed the PRD, API endpoints, and database schema to generate UI architecture decisions for the Simple Issue Tracker MVP. 30 questions were addressed with recommendations accepted for implementation.

---

## Questions & Recommendations

### 1. Dashboard Structure
**Q:** How should the dashboard home view be structured given the multiple data sources?
**R:** Widget-based layout with three sections: board list panel, standby queue alert/badge, recent tickets feed. Use RTK Query for `/api/dashboard/stats` and `/api/tickets/recent` with independent cache invalidation.

### 2. Navigation Pattern
**Q:** What navigation pattern for manager portal given board → tickets → ticket detail hierarchy?
**R:** Sidebar navigation (Dashboard, Boards, Standby Queue, Settings). Breadcrumbs for Board List → Board Detail → Ticket Detail. Sidebar persistent on desktop, collapsible on mobile.

### 3. State Management & Cache Invalidation
**Q:** How to handle board-level ticket counts vs filtered ticket lists to avoid stale data?
**R:** RTK Query with tag-based invalidation. On ticket state change, invalidate both ticket list and parent board cache. Use optimistic updates for state changes.

### 4. Loading & Error States
**Q:** What patterns for API-dependent components, especially inbox connection testing (10s timeout)?
**R:** Consistent loading state system via React context. Progress indicator with cancel for long operations. Inline errors with retry. Show individual IMAP/SMTP status indicators.

### 5. Public Form Error Handling
**Q:** How should public ticket form handle 404/410/403 errors?
**R:** Distinct UI states: 404 = "form not available", 410 = "no longer accepting tickets", 403 = display manager's suspension message. Never expose internal details.

### 6. Real-time vs Polling
**Q:** Real-time updates vs polling for standby queue and dashboard?
**R:** Background polling via RTK Query `pollingInterval` (60 seconds). Aligns with email processing frequency, avoids WebSocket complexity for MVP.

### 7. Ticket State Transitions UI
**Q:** How to enforce valid state flows while remaining intuitive?
**R:** Display only valid next-state options. Dropdown on list view, buttons on detail view. Confirmation modal for state changes (especially reject) with optional comment field.

### 8. Email Inbox Form Validation
**Q:** Validation strategy for complex inbox configuration forms?
**R:** React Hook Form for immediate feedback. IMAP/SMTP in collapsible sections. Two-step flow: test connection via `/api/inboxes/test`, then save only on success.

### 9. Timezone Handling
**Q:** How should timezone handling work across the application?
**R:** Store manager timezone in Redux after login. Shared `formatDateTime` utility converts UTC to manager timezone. Public views use browser timezone via `Intl.DateTimeFormat`.

### 10. Keyword Conflict Validation
**Q:** Strategy for keyword conflict errors from another board?
**R:** Parse 409 error message containing board name. Display inline error with link to conflicting board for contextual resolution.

### 11. Email Verification Flow
**Q:** How to handle email verification requirement before login?
**R:** On 403 with unverified email, redirect to "Verify Your Email" page with resend button, 60-second countdown timer. Store pending email in sessionStorage.

### 12. Account Suspension Flow
**Q:** UX pattern for irreversible account suspension (3-step confirmation)?
**R:** Multi-step modal wizard: (1) suspension message input, (2) password confirmation, (3) final warning requiring user to type "SUSPEND". Danger-colored styling throughout.

### 13. External Platform Configuration
**Q:** How to handle conditional Jira/Trello configuration fields?
**R:** Radio buttons for platform selection. Dynamic reveal of platform-specific fields. "Test Connection" button required before save when external platform configured.

### 14. Pagination Pattern
**Q:** Infinite scroll or traditional pagination for ticket lists?
**R:** Traditional numbered pagination (10/25/50 per page). Page size selector in localStorage. "Jump to page" input. Preserve pagination in URL query params.

### 15. Filter Panel Design
**Q:** How to balance filter power with usability?
**R:** Collapsible filter panel: state multi-select checkboxes, date range picker, title/description search. Active filter count badge. "Clear All" action. Persist per-board in localStorage.

### 16. Mobile-First Dashboard
**Q:** Mobile-first approach using Bootstrap grid?
**R:** Stack widgets vertically on mobile (<768px): board list as accordion, standby queue as alert banner, tickets as card list. 2-3 column grid on tablet/desktop. 44x44px minimum touch targets.

### 17. Standby Queue Actions
**Q:** How to present assign-to-board and retry-external actions?
**R:** Full email content display. Two action sections: "Assign to Board" dropdown + confirm, "Retry External" (if applicable). "Discard" with confirmation modal.

### 18. i18n Implementation
**Q:** Pattern for EN/PL language switching?
**R:** react-i18next with JSON files. Detection: localStorage → browser language → English fallback. Language switcher in header. Public forms use browser detection. API calls include Accept-Language header.

### 19. Public Ticket Status History
**Q:** How to display status changes to end users?
**R:** Vertical timeline component showing state transitions chronologically. Timestamp, state change text, manager comment if provided. Color-coded badges with text labels. Read-only.

### 20. Board List Caching
**Q:** Caching strategy for dashboard board list?
**R:** RTK Query with 30-second cache, stale-while-revalidate. Immediate invalidation on board/ticket changes. Subtle "Updating..." indicator during background refetch.

### 21. JWT Token Refresh
**Q:** How to handle token refresh transparently?
**R:** Axios interceptor: detect 401, call `/api/auth/refresh`, retry request. Queue concurrent requests during refresh. On refresh failure, clear auth and redirect to login. Store tokens in memory (not localStorage).

### 22. Component Architecture
**Q:** Component architecture for reusable UI elements?
**R:** Shared library at `src/components/common/`: Button, Card, Modal, Form controls, Badge, Alert, Spinner, Pagination, EmptyState. Public views use minimal subset without navigation chrome.

### 23. Empty States
**Q:** Design for empty boards, queue, new accounts?
**R:** Contextual empty states: illustration, explanatory text, CTA. "No tickets" → share link. "Queue empty" → success indicator. "No boards" → create board button. Avoid generic "No data".

### 24. Destructive Action Confirmations
**Q:** Confirmation patterns for delete/discard/reject?
**R:** Danger-styled modal: action description, consequences, Cancel + red action button. Show ticket counts for board deletion. Disable delete if non-rejected tickets exist, suggest archive.

### 25. Settings Organization
**Q:** How to organize profile/settings section?
**R:** Tabbed/sidebar navigation: Profile, Security, Email Inboxes. Separate routes (`/settings/profile`, etc.). Inbox config in slide-out panel or dedicated page. Breadcrumbs for nested views.

### 26. Toast Notifications
**Q:** Toast pattern for async operation feedback?
**R:** ToastContext, top-right positioning. Auto-dismiss success (5s), persist errors. Types: success/error/warning/info. Progress toasts for multi-step operations. Max 3 visible, stacked vertically.

### 27. Keyboard & Accessibility
**Q:** Keyboard navigation and accessibility implementation?
**R:** WCAG 2.1 AA compliance. Visible focus indicators, semantic HTML, aria-labels for icon buttons. Arrow key navigation for dropdowns. Skip-to-content link. Screen reader testing. Text + color for states.

### 28. Browser Navigation
**Q:** Handle back/forward navigation for filtered views?
**R:** React Router with URL query params: `/boards/{id}/tickets?state=new&page=2&sort=created_at`. Update URL on filter change via `useSearchParams`. Enables bookmarking and sharing.

### 29. URL Slug Validation
**Q:** Real-time validation for board unique_name?
**R:** Debounced validation (300ms): client-side regex check, optional backend uniqueness check. Inline validation indicators. Auto-suggest slug from board name.

### 30. Error Boundaries
**Q:** Error boundary strategy for production?
**R:** Three levels: App-level (full page error), Route-level (allow navigation elsewhere), Widget-level (isolate dashboard widget failures). Log to backend. User-friendly messages in production.

---

## Next Steps

1. Create detailed UI component specifications
2. Design wireframes/mockups for key views
3. Implement component library
4. Build out routes and pages
