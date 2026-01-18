# Simple Issue Tracker - Project Requirements Document

## 1. Project Overview

**Project Name:** Simple Issue Tracker

**Description:** A web application that enables managers to create ticket boards for collecting and tracking issues from users. Tickets can be created via web forms, email, or mobile application (future). The system supports either internal ticket management or forwarding to external platforms (Jira, Trello).

**Tech Stack:**
- **Frontend:** React (JavaScript), Redux, Bootstrap (responsive)
- **Backend:** Python 3.13, FastAPI, SQLAlchemy, Alembic
- **Database:** PostgreSQL
- **Deployment:** Self-contained Docker container on DigitalOcean
- **Node Version:** 22
- **Logging:** GELF format

---

## 2. User Roles

### 2.1 Manager (Ticket Board Manager)
- Authenticated via email/password with JWT tokens
- Can create and manage ticket boards
- Can change ticket statuses
- Can configure email inboxes (IMAP/SMTP)
- Can configure external platform integrations per board
- Has access to personal dashboard and standby queue

### 2.2 User (Typical User)
- **Not authenticated**
- Can create tickets via:
  - Public web form on board URL
  - Email to manager's configured inbox
  - Mobile application (future phase)
- Can view only their own tickets via secret UUID-based URLs
- Cannot view full ticket boards

---

## 3. Functional Requirements

### 3.1 Manager Registration & Authentication

| Requirement | Details |
|-------------|---------|
| Registration fields | Email, password, name |
| Email verification | Required via single-use URL |
| Password requirements | Minimum 8 characters |
| Authentication method | JWT tokens |
| Token expiry | 24 hours (configurable via env variable) |
| Token refresh | Refreshes on use |
| Password reset | Via email link |
| Account deletion | Not available - only suspension |

### 3.2 Manager Account Suspension

- Manager can self-suspend (no reactivation possible)
- Suspension flow:
  1. Manager enters suspension message (required)
  2. Manager confirms with password
  3. Final "are you sure" confirmation modal
- Upon suspension:
  - Web forms for all boards become disabled with suspension message displayed
  - Incoming emails receive auto-reply with suspension message
  - Existing tickets remain publicly viewable via secret links

### 3.3 Manager Profile Configuration

| Setting | Details |
|---------|---------|
| Name | Editable |
| Password | Changeable |
| Email inboxes | Multiple configurable (IMAP/SMTP) |
| Timezone | Default from browser, configurable in profile |

### 3.4 Email Inbox Configuration

- Managers can configure multiple email inboxes
- Each inbox requires IMAP and SMTP credentials
- Inboxes can optionally be assigned exclusively to specific boards
- Polling frequency: configurable per inbox (1, 5, or 15 minutes)
- "Test connection" button for validation before saving
- Connection failures: retry silently and log

### 3.5 Ticket Boards

#### Board Properties
| Property | Details |
|----------|---------|
| Name | Required |
| Unique name | URL-safe slug for public form URL (`/board/{unique-name}`), must be globally unique |
| Keywords | For email subject matching (free-form) |
| Greeting message | Displayed above public web form |
| Exclusive inbox | Optional - assign specific inbox to board |
| External platform config | Optional - Jira or Trello settings |

#### Board Visibility
- Boards are **not publicly visible**
- Only tickets are publicly accessible via secret URLs

#### Board Lifecycle
| Action | Condition |
|--------|-----------|
| Delete | Only allowed if all tickets are in "rejected" state (or no tickets) |
| Archive | Required if any tickets exist in non-rejected states |
| Unarchive | Not available |

When a board is deleted, all its tickets are deleted.

#### Keyword Validation
- Keywords must be unique across all of a manager's boards
- **Hard validation** - conflicting keywords are blocked entirely
- Keywords are matched against email subject lines

### 3.6 Tickets

#### Ticket Fields
| Field | Details |
|-------|---------|
| Title | Max 255 characters |
| Description | Max 6,000 characters |
| State | new, in_progress, closed, rejected |
| Creator email | Captured from form/email sender |
| Creation date | Stored in UTC |

#### State Transitions
```
Path A: new → in_progress → closed
                         → rejected

Path B: new → rejected
```

#### Ticket Properties
- Cannot be edited (only state changes allowed)
- Cannot be deleted by managers
- No attachments in this iteration
- No commenting/conversation threads
- No assignment between managers
- Secret links do not expire

#### State Change
- Manager can add optional comment when changing state
- User receives email notification on every state change (includes comment if provided)

### 3.7 Ticket Creation

#### Via Web Form
- Form URL: `/board/{unique-name}` (unique-name is a URL-safe slug per board)
- Form fields: email (required), title (required), description (required)
- Validation: email format, title max 255 chars, description max 6,000 chars
- Inline error display per field
- On success: success message displayed + confirmation email sent

#### Via Email
- Parsed as: subject → title, body → description
- HTML bodies stripped to plain text
- Sender email extracted automatically
- Duplicate prevention: same sender + same subject within configurable threshold (env variable) = ignored
- Confirmation email sent on successful creation

#### Email Routing Priority
1. Sender address matches inbox assigned exclusively to a board
2. Subject keyword matching (only on boards without exclusive inbox assignment)
3. If no match: ticket placed in manager's **standby queue**

### 3.8 Standby Queue

- Per-manager queue for:
  - Emails that couldn't be routed to a specific board
  - Failed external platform ticket creations
- Manager actions on queued tickets:
  - Assign to a board (internal)
  - Retry external platform creation
  - Move to internal board after failed external creation

### 3.9 External Platform Integration

#### Supported Platforms
- Jira Cloud (Server/Data Center not supported)
- Trello

#### Configuration (per board)
| Platform | Required Config |
|----------|-----------------|
| Jira | Instance URL, project key, API token |
| Trello | Board ID, API key, token |

- "Test connection" button before saving configuration

#### Behavior
- One-way integration only (create + redirect)
- No status sync back from external platforms
- Field mapping:
  - Title → Summary (Jira) / Card name (Trello)
  - Description → Description
  - Creator email → Dedicated field if available, otherwise appended to description

#### On External Creation Failure
- Ticket placed in manager's standby queue
- Manager can retry or move to internal board

#### Local Storage for External Tickets
| Field | Stored |
|-------|--------|
| Creation date | Yes |
| Title | Yes |
| Sender email | Yes |
| External URL | Yes (for redirect) |

External ticket stubs kept indefinitely.

### 3.10 Notifications (Email)

| Event | Recipient | Content |
|-------|-----------|---------|
| Ticket created | User (creator) | Confirmation with ticket title, description, secret link, board name |
| Status changed | User (creator) | New status + optional manager comment + secret link |

- Sent from: manager's configured inbox address
- Format: plain text
- Include secret ticket link: yes

### 3.11 Manager Dashboard

#### Main Dashboard Content
- List of boards
- Standby queue count
- Recent tickets

#### Ticket List Features
- Pagination: numbered pages
- Default page size: configurable (10, 25, 50)
- Filters: title, state, date range, description content
- Ordering: date created, title, state, last updated

---

## 4. Technical Requirements

### 4.1 API Design

- Single API serving both web and future mobile applications
- RESTful design
- Auto-generated documentation via FastAPI (Swagger/OpenAPI)
- Health endpoint: `GET /health` (no rate limiting)

### 4.2 Authentication & Security

| Aspect | Implementation |
|--------|----------------|
| Manager auth | JWT tokens |
| Token expiry | 24 hours default (env configurable) |
| Token refresh | On use |
| User auth | None (secret links) |
| Rate limiting | Per IP |
| Rate limit whitelist | 127.0.0.1/localhost for testing |
| Password storage | Hashed (use secure algorithm) |

### 4.3 Security Headers

- X-Frame-Options: DENY (prevent clickjacking)
- X-Content-Type-Options: nosniff
- Other best-practice headers
- CSP: not required
- CORS: same-origin (frontend served from same container)

### 4.4 Database

- PostgreSQL
- ORM: SQLAlchemy
- Migrations: Alembic
- All timestamps stored in UTC

### 4.5 Email Integration

| Component | Details |
|-----------|---------|
| Incoming | IMAP connection |
| Outgoing | SMTP connection |
| Polling | Configurable per inbox (1/5/15 minutes) |
| HTML handling | Strip to plain text |
| Failure handling | Retry silently, log errors |

### 4.6 Logging

- Format: GELF
- Log IMAP connection failures
- Log general application events

### 4.7 Environment Variables

| Variable | Purpose |
|----------|---------|
| DATABASE_URL | PostgreSQL connection string |
| DATABASE_CREDENTIALS | Database auth |
| JWT_EXPIRY | Token expiry duration |
| SMTP_DEFAULTS | Default SMTP configuration |
| RATE_LIMIT_* | Rate limiting thresholds |
| DUPLICATE_EMAIL_THRESHOLD | Time window for duplicate email prevention |
| ENCRYPTION_KEY | AES-256-GCM key for encrypting sensitive data (IMAP/SMTP passwords, API tokens) |

---

## 5. Frontend Requirements

### 5.1 Technical Stack

- React (JavaScript)
- Redux for state management
- Bootstrap (responsive design)
- Node 22 for build

### 5.2 Internationalization (i18n)

- Languages: English, Polish
- Translations stored as JSON files in frontend
- Translation management on frontend side only

### 5.3 Responsive Design

- Manager dashboard must be mobile-friendly
- Public ticket forms must be responsive

### 5.4 UI Components

#### Public Ticket Form
- Greeting message displayed above form
- Fields: email, title, description
- Inline validation errors
- Success message on submission

#### Manager Dashboard
- Board list with quick actions
- Standby queue indicator with count
- Recent tickets section
- Navigation to settings/profile

#### Ticket Management
- Paginated ticket list
- Filter panel (title, state, date range, description)
- Sort options (date, title, state, last updated)
- State change: dropdown on board view, buttons on ticket details

#### Board Management
- Create/edit board modal
- Keyword configuration with conflict validation
- External platform configuration with test connection
- Greeting message editor

### 5.5 Timezone Display

- Managers: browser default, configurable in profile
- Users: browser settings

---

## 6. Deployment

### 6.1 Infrastructure

- Self-contained Docker container
- Frontend served from same container as backend (no separate CDN)
- Hosted on DigitalOcean

### 6.2 Docker Configuration

- Python 3.13 base
- Node 22 for frontend build
- Single container architecture

---

## 7. Testing

- Unit tests required
- Focus on business logic and API endpoints

---

## 8. URL Structure

| Endpoint | Purpose |
|----------|---------|
| `/health` | Health check (no rate limiting) |
| `/board/{unique-name}` | Public ticket creation form |
| `/ticket/{uuid}` | Public ticket view (secret link) |
| `/api/*` | API endpoints |
| `/*` | Frontend SPA routes |

---

## 9. Data Model (Conceptual)

### Manager
- id, email, password_hash, name, timezone, suspension_message, is_suspended, created_at

### EmailInbox
- id, manager_id, imap_host, imap_credentials, smtp_host, smtp_credentials, polling_interval, exclusive_board_id

### Board
- id, manager_id, name, unique_name (URL slug), greeting_message, is_archived, external_platform_type, external_platform_config, created_at

### BoardKeyword
- id, board_id, keyword

### Ticket
- id, board_id, uuid (secret), title, description, state, creator_email, created_at, updated_at (reflects last status change)

### TicketStatusChange
- id, ticket_id, previous_state, new_state, comment (optional), created_at

### ExternalTicket
- id, board_id, uuid (secret), title, creator_email, external_url, created_at

**Note:** UUID must be unique across both Ticket and ExternalTicket tables. Enforced at application level: on generation, check both tables for conflicts and retry with new UUID if collision detected.

### StandbyQueueItem
- id, manager_id, email_subject, email_body, sender_email, failure_reason, created_at

---

## 10. Out of Scope (This Iteration)

- Mobile application (keep API compatible for future)
- File attachments on tickets
- Ticket conversation threads (note: single manager comment on status change IS in scope)
- Multi-manager boards
- Ticket assignment between managers
- Jira Server/Data Center support
- Status sync from external platforms
- Account reactivation after suspension
- Board unarchiving
- Ticket deletion
- Ticket editing (beyond state changes)
- Custom ticket states per board
- Super-admin role
- CDN for static assets

---

## 11. Future Considerations

- Mobile application (React Native or native) using same API
- Additional external platform integrations
- File attachments
- Ticket commenting system
- Advanced notification preferences
- Custom branding for email templates
- Multi-manager board collaboration

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-17 | AI-assisted | Initial draft |
| 0.2 | 2026-01-17 | AI-assisted | Added ENCRYPTION_KEY environment variable for AES-256-GCM encryption |
| 0.3 | 2026-01-17 | AI-assisted | Clarified UUID uniqueness is enforced at application level |
