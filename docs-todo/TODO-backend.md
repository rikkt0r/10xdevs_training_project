# Backend Implementation TODO

**Overall Status: ~90% complete**

## Missing API Endpoints

| Endpoint | Method | Priority |
|----------|--------|----------|
| `/api/boards/{board_id}/external-tickets` | GET | High |
| `/api/external-tickets/{id}` | GET | High |

## Missing Features

### Critical - External Platform Integration

- [ ] **Jira Cloud connector** (`app/services/external_platforms/jira.py`)
  - API client implementation
  - Ticket creation with field mapping (title → summary, description, creator email)
  - Test connection logic (currently stubbed in board_service)

- [ ] **Trello connector** (`app/services/external_platforms/trello.py`)
  - API client implementation
  - Card creation with field mapping
  - Test connection logic (currently stubbed in board_service)

- [ ] **External ticket creation flow**
  - Create ticket in external platform on board submission
  - Store external_ticket record with URL
  - On failure → move to standby queue

### Critical - Email Polling Engine

- [ ] **Background IMAP polling service**
  - Periodic task (1/5/15 min intervals per inbox)
  - Connection management and retry logic
  - Error logging (GELF format)

- [ ] **Email parsing and routing**
  - Parse subject → title, body → description, sender → creator_email
  - HTML stripping to plain text
  - Keyword matching against email subjects
  - Exclusive inbox routing priority
  - Fallback to standby queue when no match

- [ ] **Duplicate email prevention**
  - Check processed_emails table (sender + subject_hash within threshold)
  - Record processed emails after successful creation

## Completed Features

- All 10 database models with migrations
- 55/56 API endpoints implemented
- JWT authentication with refresh
- Email verification and password reset
- Rate limiting (per-IP, endpoint-specific)
- Security headers middleware
- AES encryption for sensitive data (IMAP/SMTP passwords, API tokens)
- Board CRUD with archive/delete logic
- Ticket CRUD with state transitions
- Standby queue assign/retry/delete operations
- Public ticket form and view
- Dashboard statistics
- Email inbox configuration with connection testing
- Pydantic request/response validation
- Generic response wrappers (DataResponse, PaginatedDataResponse)
- **Status change email notifications** (sends email via BackgroundTasks on ticket state change)
- **Ticket creation confirmation emails** (sends email via BackgroundTasks on public form submission)
- **UUID uniqueness enforcement** (`generate_unique_ticket_uuid()` in `core/security.py` checks both tickets and external_tickets tables)

## Test Coverage Gaps

- [ ] External platform integration tests (once implemented)
- [ ] Email polling service tests (once implemented)
- [ ] Board/ticket endpoint tests (missing)
- [ ] Integration tests for full ticket creation flow

---

*Last updated: 2026-01-21*
