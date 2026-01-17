# API Endpoint Specification

## Overview

RESTful API for the Simple Issue Tracker application. All endpoints are prefixed with `/api` except for public-facing pages and health check.

**Base URL:** `/api`

---

## Authentication

- **Manager endpoints:** Require JWT token in `Authorization: Bearer <token>` header
- **Public endpoints:** No authentication required
- **Rate limiting:** Applied per IP address (127.0.0.1/localhost whitelisted for testing)

---

## Common Response Formats

### Success Response (Single Resource)
```json
{
  "data": { ... }
}
```

### Success Response (List)
```json
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 25,
    "total_items": 150,
    "total_pages": 6
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable error message",
    "details": { ... }
  }
}
```

### Common HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success (GET, PUT, PATCH) |
| 201 | Created (POST) |
| 204 | No Content (DELETE) |
| 400 | Bad Request / Validation Error |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (valid token, insufficient permissions) |
| 404 | Resource Not Found |
| 409 | Conflict (duplicate resource) |
| 422 | Unprocessable Entity (business rule violation) |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |

---

## Endpoints

### 1. Health Check

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | None | Application health check (no rate limiting) |

**Response 200 (Healthy):**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-17T12:00:00Z"
}
```

**Response 503 (Unhealthy):**
```json
{
  "status": "unhealthy",
  "timestamp": "2026-01-17T12:00:00Z",
  "details": {
    "database": {
      "status": "unhealthy",
      "message": "Connection refused"
    },
    "email_polling": {
      "status": "healthy",
      "message": null
    }
  }
}
```

**Notes:**
- `details` object is only included when `status` is `unhealthy`
- Each component reports its own status and optional failure message

---

### 2. Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST   | `/api/auth/register` | None | Register new manager account |
| POST   | `/api/auth/login` | None | Authenticate and receive JWT token |
| POST   | `/api/auth/logout` | JWT | Invalidate current token |
| GET    | `/api/auth/verify-email` | None | Verify email with token |
| POST   | `/api/auth/resend-verification` | None | Resend verification email |
| POST   | `/api/auth/forgot-password` | None | Request password reset email |
| POST   | `/api/auth/reset-password` | None | Reset password with token |
| POST   | `/api/auth/refresh` | JWT | Refresh JWT token |

#### POST `/api/auth/register`

**Request Body:**
```json
{
  "email": "manager@example.com",
  "password": "securePassword123",
  "name": "John Doe"
}
```

**Validation:**
- `email`: Valid email format, unique
- `password`: Minimum 8 characters
- `name`: Required, max 255 characters

**Response 201:**
```json
{
  "data": {
    "id": 1,
    "email": "manager@example.com",
    "name": "John Doe",
    "email_verified": false,
    "created_at": "2026-01-17T12:00:00Z"
  },
  "message": "Verification email sent"
}
```

#### POST `/api/auth/login`

**Request Body:**
```json
{
  "email": "manager@example.com",
  "password": "securePassword123"
}
```

**Response 200:**
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 86400,
    "manager": {
      "id": 1,
      "email": "manager@example.com",
      "name": "John Doe",
      "timezone": "Europe/Warsaw"
    }
  }
}
```

**Error 401:** Invalid credentials
**Error 403:** Account suspended or email not verified

#### POST `/api/auth/verify-email`

**Request Body:**
```json
{
  "token": "verification-token-from-email"
}
```

**Response 200:**
```json
{
  "message": "Email verified successfully"
}
```

#### POST `/api/auth/forgot-password`

**Request Body:**
```json
{
  "email": "manager@example.com"
}
```

**Response 200:** Always returns success (prevents email enumeration)
```json
{
  "message": "If the email exists, a reset link has been sent"
}
```

#### POST `/api/auth/reset-password`

**Request Body:**
```json
{
  "token": "reset-token-from-email",
  "password": "newSecurePassword123"
}
```

**Response 200:**
```json
{
  "message": "Password reset successfully"
}
```

---

### 3. Manager Profile

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/me` | JWT | Get current manager profile |
| PATCH | `/api/me` | JWT | Update profile (name, timezone) |
| PUT | `/api/me/password` | JWT | Change password |
| POST | `/api/me/suspend` | JWT | Suspend own account |

#### GET `/api/me`

**Response 200:**
```json
{
  "data": {
    "id": 1,
    "email": "manager@example.com",
    "name": "John Doe",
    "timezone": "Europe/Warsaw",
    "is_suspended": false,
    "email_verified_at": "2026-01-17T12:00:00Z",
    "created_at": "2026-01-17T10:00:00Z"
  }
}
```

#### PATCH `/api/me`

**Request Body:**
```json
{
  "name": "John Smith",
  "timezone": "America/New_York"
}
```

**Response 200:** Updated profile object

#### PUT `/api/me/password`

**Request Body:**
```json
{
  "current_password": "oldPassword123",
  "new_password": "newPassword456"
}
```

**Response 200:**
```json
{
  "message": "Password changed successfully"
}
```

#### POST `/api/me/suspend`

**Request Body:**
```json
{
  "suspension_message": "This service is no longer available.",
  "password": "currentPassword123"
}
```

**Response 200:**
```json
{
  "message": "Account suspended successfully"
}
```

**Note:** This action is irreversible. All board forms will be disabled.

---

### 4. Email Inboxes

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/inboxes` | JWT | List all configured inboxes |
| POST | `/api/inboxes` | JWT | Create new inbox configuration |
| GET | `/api/inboxes/{id}` | JWT | Get inbox details |
| PUT | `/api/inboxes/{id}` | JWT | Update inbox configuration |
| DELETE | `/api/inboxes/{id}` | JWT | Delete inbox |
| POST | `/api/inboxes/{id}/test` | JWT | Test inbox connection |
| POST | `/api/inboxes/test` | JWT | Test connection with provided credentials (before save) |

#### GET `/api/inboxes`

**Response 200:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Support Inbox",
      "from_address": "support@example.com",
      "imap_host": "imap.example.com",
      "imap_port": 993,
      "smtp_host": "smtp.example.com",
      "smtp_port": 587,
      "polling_interval": 5,
      "is_active": true,
      "last_polled_at": "2026-01-17T11:55:00Z",
      "exclusive_board_id": null,
      "created_at": "2026-01-17T10:00:00Z"
    }
  ]
}
```

#### POST `/api/inboxes`

**Request Body:**
```json
{
  "name": "Support Inbox",
  "imap_host": "imap.example.com",
  "imap_port": 993,
  "imap_username": "support@example.com",
  "imap_password": "imapPassword",
  "imap_use_ssl": true,
  "smtp_host": "smtp.example.com",
  "smtp_port": 587,
  "smtp_username": "support@example.com",
  "smtp_password": "smtpPassword",
  "smtp_use_tls": true,
  "from_address": "support@example.com",
  "polling_interval": 5,
  "exclusive_board_id": null
}
```

**Validation:**
- `polling_interval`: Must be 1, 5, or 15
- `exclusive_board_id`: Must be a board owned by the manager (or null)

**Response 201:** Created inbox object (passwords not returned)

#### POST `/api/inboxes/test`

Test connection before saving inbox configuration.

**Request Body:**
```json
{
  "imap_host": "imap.example.com",
  "imap_port": 993,
  "imap_username": "support@example.com",
  "imap_password": "imapPassword",
  "imap_use_ssl": true,
  "smtp_host": "smtp.example.com",
  "smtp_port": 587,
  "smtp_username": "support@example.com",
  "smtp_password": "smtpPassword",
  "smtp_use_tls": true
}
```

**Response 200 (All tests passed):**
```json
{
  "data": {
    "imap_status": "success",
    "smtp_status": "success"
  }
}
```

**Response 422 (Connection failed):**
```json
{
  "data": {
    "imap_status": "failed",
    "imap_error": "Authentication failed: Invalid credentials for support@example.com",
    "smtp_status": "success"
  }
}
```

**Alternative Response 422 (Multiple failures):**
```json
{
  "data": {
    "imap_status": "failed",
    "imap_error": "Connection timeout: imap.example.com:993 did not respond within 10 seconds",
    "smtp_status": "failed",
    "smtp_error": "TLS negotiation failed on smtp.example.com:587"
  }
}
```

**Notes:**
- Both IMAP and SMTP connections are tested independently
- Tests run in parallel for faster response
- Timeout for each test: 10 seconds
- Error messages include relevant details (host, port, credentials used, etc.) in a human-readable format

#### POST `/api/inboxes/{id}/test`

Test connection for existing inbox (uses stored credentials).

**Response 200/422:** Same format as `/api/inboxes/test` above

**Notes:**
- Uses stored encrypted credentials from the database
- Does not require credentials in request body
- Returns same detailed error structure as `/api/inboxes/test`

---

### 5. Boards

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/boards` | JWT | List all boards |
| POST | `/api/boards` | JWT | Create new board |
| GET | `/api/boards/{id}` | JWT | Get board details |
| PUT | `/api/boards/{id}` | JWT | Update board |
| DELETE | `/api/boards/{id}` | JWT | Delete board (only if all tickets rejected or none) |
| POST | `/api/boards/{id}/archive` | JWT | Archive board |
| POST | `/api/boards/{id}/test-external` | JWT | Test external platform connection |

#### GET `/api/boards`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| include_archived | boolean | false | Include archived boards |

**Response 200:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Bug Reports",
      "unique_name": "bug-reports",
      "greeting_message": "Report a bug and we'll fix it!",
      "is_archived": false,
      "external_platform_type": null,
      "exclusive_inbox_id": null,
      "ticket_counts": {
        "new": 5,
        "in_progress": 3,
        "closed": 20,
        "rejected": 2
      },
      "created_at": "2026-01-17T10:00:00Z"
    }
  ]
}
```

#### POST `/api/boards`

**Request Body:**
```json
{
  "name": "Bug Reports",
  "unique_name": "bug-reports",
  "greeting_message": "Report a bug and we'll fix it!",
  "exclusive_inbox_id": null,
  "external_platform_type": null,
  "external_platform_config": null
}
```

**Validation:**
- `name`: Required, max 255 characters
- `unique_name`: Required, URL-safe slug (lowercase alphanumeric and hyphens), globally unique
- `greeting_message`: Optional, text
- `external_platform_type`: null, "jira", or "trello"
- `external_platform_config`: Required if external_platform_type is set

**External Platform Config (Jira):**
```json
{
  "external_platform_type": "jira",
  "external_platform_config": {
    "instance_url": "https://company.atlassian.net",
    "project_key": "BUG",
    "api_token": "jira-api-token"
  }
}
```

**External Platform Config (Trello):**
```json
{
  "external_platform_type": "trello",
  "external_platform_config": {
    "board_id": "abc123",
    "api_key": "trello-api-key",
    "api_token": "trello-api-token"
  }
}
```

**Response 201:** Created board object

**Error 409:** unique_name already exists

#### DELETE `/api/boards/{id}`

**Response 204:** Board deleted

**Error 422:** Board has tickets in non-rejected states (must archive instead)
```json
{
  "error": {
    "code": "BOARD_HAS_ACTIVE_TICKETS",
    "message": "Cannot delete board with active tickets. Archive the board instead."
  }
}
```

#### POST `/api/boards/{id}/archive`

**Response 200:**
```json
{
  "data": {
    "id": 1,
    "is_archived": true,
    ...
  }
}
```

#### POST `/api/boards/{id}/test-external`

Test external platform connection for a configured board.

**Response 200:**
```json
{
  "data": {
    "status": "success",
    "message": "Successfully connected to Jira project BUG"
  }
}
```

**Error 422:**
```json
{
  "error": {
    "code": "EXTERNAL_CONNECTION_FAILED",
    "message": "Failed to connect to Jira: Invalid API token"
  }
}
```

---

### 6. Board Keywords

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/boards/{board_id}/keywords` | JWT | List keywords for board |
| POST | `/api/boards/{board_id}/keywords` | JWT | Add keyword to board |
| DELETE | `/api/boards/{board_id}/keywords/{id}` | JWT | Remove keyword from board |

#### GET `/api/boards/{board_id}/keywords`

**Response 200:**
```json
{
  "data": [
    {
      "id": 1,
      "keyword": "bug",
      "created_at": "2026-01-17T10:00:00Z"
    },
    {
      "id": 2,
      "keyword": "error",
      "created_at": "2026-01-17T10:00:00Z"
    }
  ]
}
```

#### POST `/api/boards/{board_id}/keywords`

**Request Body:**
```json
{
  "keyword": "crash"
}
```

**Response 201:** Created keyword object

**Error 409:** Keyword already exists on another board owned by this manager
```json
{
  "error": {
    "code": "KEYWORD_CONFLICT",
    "message": "Keyword 'crash' is already assigned to board 'Critical Issues'"
  }
}
```

---

### 7. Tickets (Manager)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/boards/{board_id}/tickets` | JWT | List tickets for board |
| GET | `/api/tickets/{id}` | JWT | Get ticket details |
| PATCH | `/api/tickets/{id}/state` | JWT | Change ticket state |
| GET | `/api/tickets/recent` | JWT | Get recent tickets across all boards |

#### GET `/api/boards/{board_id}/tickets`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number |
| limit | integer | 25 | Items per page (10, 25, 50) |
| state | string | - | Filter by state (comma-separated for multiple) |
| title | string | - | Search in title (partial match) |
| description | string | - | Search in description (partial match) |
| date_from | string | - | Filter by creation date (ISO 8601) |
| date_to | string | - | Filter by creation date (ISO 8601) |
| sort_by | string | created_at | Sort field: created_at, title, state, updated_at |
| sort_order | string | desc | Sort order: asc, desc |

**Response 200:**
```json
{
  "data": [
    {
      "id": 1,
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Login button not working",
      "description": "When I click the login button, nothing happens...",
      "state": "new",
      "creator_email": "user@example.com",
      "source": "web",
      "created_at": "2026-01-17T10:00:00Z",
      "updated_at": "2026-01-17T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 25,
    "total_items": 150,
    "total_pages": 6
  }
}
```

#### GET `/api/tickets/{id}`

**Response 200:**
```json
{
  "data": {
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "board": {
      "id": 1,
      "name": "Bug Reports",
      "unique_name": "bug-reports"
    },
    "title": "Login button not working",
    "description": "When I click the login button, nothing happens...",
    "state": "new",
    "creator_email": "user@example.com",
    "source": "web",
    "created_at": "2026-01-17T10:00:00Z",
    "updated_at": "2026-01-17T10:00:00Z",
    "status_changes": [
      {
        "id": 1,
        "previous_state": "new",
        "new_state": "in_progress",
        "comment": "Looking into this issue",
        "created_at": "2026-01-17T11:00:00Z"
      }
    ]
  }
}
```

#### PATCH `/api/tickets/{id}/state`

**Request Body:**
```json
{
  "state": "in_progress",
  "comment": "Looking into this issue"
}
```

**Validation:**
- `state`: Required, valid state transition
- `comment`: Optional, text

**Valid State Transitions:**
- `new` → `in_progress`, `rejected`
- `in_progress` → `closed`, `rejected`

**Response 200:** Updated ticket object

**Error 422:** Invalid state transition
```json
{
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "message": "Cannot transition from 'closed' to 'in_progress'"
  }
}
```

#### GET `/api/tickets/recent`

Get recent tickets across all manager's boards for dashboard.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 10 | Number of tickets to return (max 50) |

**Response 200:**
```json
{
  "data": [
    {
      "id": 1,
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Login button not working",
      "state": "new",
      "board": {
        "id": 1,
        "name": "Bug Reports"
      },
      "created_at": "2026-01-17T10:00:00Z"
    }
  ]
}
```

---

### 8. External Tickets (Manager)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/boards/{board_id}/external-tickets` | JWT | List external tickets for board |
| GET | `/api/external-tickets/{id}` | JWT | Get external ticket details |

#### GET `/api/boards/{board_id}/external-tickets`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number |
| limit | integer | 25 | Items per page |

**Response 200:**
```json
{
  "data": [
    {
      "id": 1,
      "uuid": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Critical bug in production",
      "creator_email": "user@example.com",
      "external_url": "https://company.atlassian.net/browse/BUG-123",
      "external_id": "BUG-123",
      "platform_type": "jira",
      "created_at": "2026-01-17T10:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

### 9. Standby Queue

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/standby-queue` | JWT | List items in standby queue |
| GET | `/api/standby-queue/{id}` | JWT | Get queue item details |
| POST | `/api/standby-queue/{id}/assign` | JWT | Assign to internal board |
| POST | `/api/standby-queue/{id}/retry` | JWT | Retry external platform creation |
| DELETE | `/api/standby-queue/{id}` | JWT | Discard queue item |

#### GET `/api/standby-queue`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number |
| limit | integer | 25 | Items per page |

**Response 200:**
```json
{
  "data": [
    {
      "id": 1,
      "email_subject": "Help needed with login",
      "email_body": "I cannot log into my account...",
      "sender_email": "user@example.com",
      "failure_reason": "no_keyword_match",
      "original_board_id": null,
      "retry_count": 0,
      "created_at": "2026-01-17T10:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

#### POST `/api/standby-queue/{id}/assign`

Assign queue item to an internal board (creates ticket).

**Request Body:**
```json
{
  "board_id": 1
}
```

**Response 200:**
```json
{
  "data": {
    "ticket": {
      "id": 10,
      "uuid": "770e8400-e29b-41d4-a716-446655440002",
      "title": "Help needed with login",
      "board_id": 1
    }
  },
  "message": "Ticket created successfully"
}
```

#### POST `/api/standby-queue/{id}/retry`

Retry external platform creation (for items that failed external creation).

**Response 200:**
```json
{
  "data": {
    "external_ticket": {
      "id": 5,
      "external_url": "https://company.atlassian.net/browse/BUG-124",
      "external_id": "BUG-124"
    }
  },
  "message": "External ticket created successfully"
}
```

**Error 422:** Retry failed
```json
{
  "error": {
    "code": "EXTERNAL_CREATION_FAILED",
    "message": "Failed to create ticket in Jira: Rate limit exceeded"
  }
}
```

---

### 10. Public Ticket Form

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/public/boards/{unique_name}` | None | Get board info for public form |
| POST | `/api/public/boards/{unique_name}/tickets` | None | Create ticket via public form |

#### GET `/api/public/boards/{unique_name}`

Get minimal board information needed for the public form.

**Response 200:**
```json
{
  "data": {
    "name": "Bug Reports",
    "greeting_message": "Report a bug and we'll fix it!"
  }
}
```

**Error 404:** Board not found or manager suspended

**Error 410:** Board archived
```json
{
  "error": {
    "code": "BOARD_ARCHIVED",
    "message": "This board is no longer accepting new tickets"
  }
}
```

#### POST `/api/public/boards/{unique_name}/tickets`

**Request Body:**
```json
{
  "email": "user@example.com",
  "title": "Login button not working",
  "description": "When I click the login button, nothing happens. I've tried Chrome and Firefox."
}
```

**Validation:**
- `email`: Required, valid email format
- `title`: Required, max 255 characters
- `description`: Required, max 6000 characters

**Response 201:**
```json
{
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Login button not working",
    "message": "Your ticket has been submitted. A confirmation email has been sent."
  }
}
```

**Error 404:** Board not found
**Error 410:** Board archived
**Error 403:** Manager suspended (returns suspension message)

---

### 11. Public Ticket View

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/public/tickets/{uuid}` | None | View ticket by secret UUID |

#### GET `/api/public/tickets/{uuid}`

**Response 200:**
```json
{
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Login button not working",
    "description": "When I click the login button, nothing happens...",
    "state": "in_progress",
    "board_name": "Bug Reports",
    "created_at": "2026-01-17T10:00:00Z",
    "updated_at": "2026-01-17T11:00:00Z",
    "status_changes": [
      {
        "previous_state": "new",
        "new_state": "in_progress",
        "comment": "Looking into this issue",
        "created_at": "2026-01-17T11:00:00Z"
      }
    ]
  }
}
```

**Note:** Works for both internal tickets and external tickets. For external tickets, includes `external_url` for redirect.

**External Ticket Response 200:**
```json
{
  "data": {
    "uuid": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Critical bug in production",
    "board_name": "Bug Reports",
    "external_url": "https://company.atlassian.net/browse/BUG-123",
    "platform_type": "jira",
    "created_at": "2026-01-17T10:00:00Z"
  }
}
```

---

### 12. Dashboard Statistics

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/dashboard/stats` | JWT | Get dashboard statistics |

#### GET `/api/dashboard/stats`

**Response 200:**
```json
{
  "data": {
    "boards_count": 5,
    "active_boards_count": 4,
    "standby_queue_count": 3,
    "tickets_by_state": {
      "new": 12,
      "in_progress": 8,
      "closed": 145,
      "rejected": 15
    },
    "recent_activity": {
      "tickets_created_today": 5,
      "tickets_created_this_week": 23
    }
  }
}
```

---

## Rate Limiting

Rate limits are applied per IP address. Responses include headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705492800
```

**Default Limits:**
| Endpoint Category | Limit |
|-------------------|-------|
| Authentication (login, register) | 10 requests/minute |
| Public ticket creation | 20 requests/minute |
| General API | 100 requests/minute |
| Health check | No limit |

---

## Security Headers

All responses include:
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

---

## Internationalization

Error messages support i18n via `Accept-Language` header:
- `en` (default)
- `pl`

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-01-17 | Initial draft |
| 0.2 | 2026-01-17 | Enhanced `/api/inboxes/test` and `/api/inboxes/{id}/test` endpoints to return detailed error messages in a single text field |
