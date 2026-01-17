# Database Schema Specification

## Overview

PostgreSQL database schema for the Simple Issue Tracker application. All timestamps are stored in UTC. Uses UUID v4 for public-facing identifiers.

---

## Tables

### 1. managers

Stores manager accounts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Internal identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Login email |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| name | VARCHAR(255) | NOT NULL | Display name |
| timezone | VARCHAR(64) | NOT NULL, DEFAULT 'UTC' | IANA timezone (e.g., 'Europe/Warsaw') |
| is_suspended | BOOLEAN | NOT NULL, DEFAULT FALSE | Account suspension flag |
| suspension_message | TEXT | NULL | Message shown when suspended |
| email_verified_at | TIMESTAMP | NULL | When email was verified (NULL = unverified) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification time |

**Indexes:**
- `idx_managers_email` on `email`

---

### 2. manager_tokens

Stores JWT refresh tokens, email verification tokens, and password reset tokens.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Internal identifier |
| manager_id | INTEGER | NOT NULL, FK → managers.id ON DELETE CASCADE | Owner |
| token_hash | VARCHAR(255) | NOT NULL | SHA-256 hash of token |
| token_type | VARCHAR(20) | NOT NULL | 'refresh', 'email_verification', 'password_reset' |
| expires_at | TIMESTAMP | NOT NULL | Expiration time |
| used_at | TIMESTAMP | NULL | When token was used (for single-use tokens) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |

**Indexes:**
- `idx_manager_tokens_hash` on `token_hash`
- `idx_manager_tokens_manager_type` on `(manager_id, token_type)`

**Constraints:**
- CHECK: `token_type IN ('refresh', 'email_verification', 'password_reset')`

---

### 3. email_inboxes

Stores configured email inboxes for managers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Internal identifier |
| manager_id | INTEGER | NOT NULL, FK → managers.id ON DELETE CASCADE | Owner |
| name | VARCHAR(255) | NOT NULL | Display name for inbox |
| imap_host | VARCHAR(255) | NOT NULL | IMAP server hostname |
| imap_port | INTEGER | NOT NULL, DEFAULT 993 | IMAP port |
| imap_username | VARCHAR(255) | NOT NULL | IMAP login |
| imap_password_encrypted | TEXT | NOT NULL | Encrypted IMAP password |
| imap_use_ssl | BOOLEAN | NOT NULL, DEFAULT TRUE | Use SSL/TLS |
| smtp_host | VARCHAR(255) | NOT NULL | SMTP server hostname |
| smtp_port | INTEGER | NOT NULL, DEFAULT 587 | SMTP port |
| smtp_username | VARCHAR(255) | NOT NULL | SMTP login |
| smtp_password_encrypted | TEXT | NOT NULL | Encrypted SMTP password |
| smtp_use_tls | BOOLEAN | NOT NULL, DEFAULT TRUE | Use STARTTLS |
| from_address | VARCHAR(255) | NOT NULL | Email address for sending |
| polling_interval | INTEGER | NOT NULL, DEFAULT 5 | Polling interval in minutes |
| last_polled_at | TIMESTAMP | NULL | Last successful poll time |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether inbox is active |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification time |

**Indexes:**
- `idx_email_inboxes_manager` on `manager_id`
- `idx_email_inboxes_active_polling` on `(is_active, last_polled_at)` WHERE `is_active = TRUE`

**Constraints:**
- CHECK: `polling_interval IN (1, 5, 15)`

---

### 4. boards

Stores ticket boards.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Internal identifier |
| manager_id | INTEGER | NOT NULL, FK → managers.id ON DELETE RESTRICT | Owner |
| name | VARCHAR(255) | NOT NULL | Display name |
| unique_name | VARCHAR(255) | UNIQUE, NOT NULL | URL slug for public form |
| greeting_message | TEXT | NULL | Message shown above public form |
| is_archived | BOOLEAN | NOT NULL, DEFAULT FALSE | Archive flag |
| external_platform_type | VARCHAR(20) | NULL | 'jira' or 'trello' |
| external_platform_config | JSONB | NULL | Platform-specific configuration |
| exclusive_inbox_id | INTEGER | NULL, FK → email_inboxes.id ON DELETE SET NULL | Exclusive inbox assignment |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification time |

**Indexes:**
- `idx_boards_manager` on `manager_id`
- `idx_boards_unique_name` on `unique_name`
- `idx_boards_exclusive_inbox` on `exclusive_inbox_id` WHERE `exclusive_inbox_id IS NOT NULL`

**Constraints:**
- CHECK: `external_platform_type IS NULL OR external_platform_type IN ('jira', 'trello')`
- CHECK: `unique_name ~ '^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'` (URL-safe slug)

**Notes on external_platform_config JSONB:**

For Jira:
```json
{
  "instance_url": "https://company.atlassian.net",
  "project_key": "PROJ",
  "api_token_encrypted": "..."
}
```

For Trello:
```json
{
  "board_id": "abc123",
  "api_key_encrypted": "...",
  "api_token_encrypted": "..."
}
```

---

### 5. board_keywords

Stores keywords for email routing to boards.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Internal identifier |
| board_id | INTEGER | NOT NULL, FK → boards.id ON DELETE CASCADE | Parent board |
| keyword | VARCHAR(255) | NOT NULL | Keyword for subject matching |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |

**Indexes:**
- `idx_board_keywords_board` on `board_id`
- `idx_board_keywords_keyword_lower` on `LOWER(keyword)`

**Constraints:**
- UNIQUE: `(board_id, keyword)` - no duplicate keywords per board

**Note:** Application layer enforces keyword uniqueness across all boards of a single manager.

---

### 6. tickets

Stores internal tickets.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Internal identifier |
| uuid | UUID | UNIQUE, NOT NULL, DEFAULT gen_random_uuid() | Public secret identifier |
| board_id | INTEGER | NOT NULL, FK → boards.id ON DELETE CASCADE | Parent board |
| title | VARCHAR(255) | NOT NULL | Ticket title |
| description | TEXT | NOT NULL | Ticket description (max 6000 chars enforced at app level) |
| state | VARCHAR(20) | NOT NULL, DEFAULT 'new' | Current state |
| creator_email | VARCHAR(255) | NOT NULL | Email of ticket creator |
| source | VARCHAR(20) | NOT NULL, DEFAULT 'web' | 'web' or 'email' |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last state change time |

**Indexes:**
- `idx_tickets_uuid` on `uuid`
- `idx_tickets_board` on `board_id`
- `idx_tickets_board_state` on `(board_id, state)`
- `idx_tickets_board_created` on `(board_id, created_at DESC)`
- `idx_tickets_creator_email` on `creator_email`

**Constraints:**
- CHECK: `state IN ('new', 'in_progress', 'closed', 'rejected')`
- CHECK: `source IN ('web', 'email')`

---

### 7. ticket_status_changes

Audit log for ticket state transitions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Internal identifier |
| ticket_id | INTEGER | NOT NULL, FK → tickets.id ON DELETE CASCADE | Parent ticket |
| previous_state | VARCHAR(20) | NOT NULL | State before change |
| new_state | VARCHAR(20) | NOT NULL | State after change |
| comment | TEXT | NULL | Optional manager comment |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Change time |

**Indexes:**
- `idx_ticket_status_changes_ticket` on `ticket_id`
- `idx_ticket_status_changes_ticket_created` on `(ticket_id, created_at DESC)`

**Constraints:**
- CHECK: `previous_state IN ('new', 'in_progress', 'closed', 'rejected')`
- CHECK: `new_state IN ('new', 'in_progress', 'closed', 'rejected')`
- CHECK: `previous_state <> new_state`

---

### 8. external_tickets

Stores references to tickets created in external platforms.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Internal identifier |
| uuid | UUID | UNIQUE, NOT NULL, DEFAULT gen_random_uuid() | Public secret identifier |
| board_id | INTEGER | NOT NULL, FK → boards.id ON DELETE CASCADE | Parent board |
| title | VARCHAR(255) | NOT NULL | Ticket title |
| creator_email | VARCHAR(255) | NOT NULL | Email of ticket creator |
| external_url | VARCHAR(2048) | NOT NULL | URL to external ticket |
| external_id | VARCHAR(255) | NULL | ID in external system |
| platform_type | VARCHAR(20) | NOT NULL | 'jira' or 'trello' |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |

**Indexes:**
- `idx_external_tickets_uuid` on `uuid`
- `idx_external_tickets_board` on `board_id`
- `idx_external_tickets_creator_email` on `creator_email`

**Constraints:**
- CHECK: `platform_type IN ('jira', 'trello')`

---

### 9. standby_queue_items

Queue for unrouted emails and failed external ticket creations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Internal identifier |
| manager_id | INTEGER | NOT NULL, FK → managers.id ON DELETE CASCADE | Owner |
| email_subject | VARCHAR(255) | NOT NULL | Original email subject |
| email_body | TEXT | NOT NULL | Original email body (plain text) |
| sender_email | VARCHAR(255) | NOT NULL | Sender's email address |
| failure_reason | VARCHAR(50) | NOT NULL | Reason for queue placement |
| original_board_id | INTEGER | NULL, FK → boards.id ON DELETE SET NULL | Board if failed external creation |
| retry_count | INTEGER | NOT NULL, DEFAULT 0 | Number of retry attempts |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update time |

**Indexes:**
- `idx_standby_queue_manager` on `manager_id`
- `idx_standby_queue_manager_created` on `(manager_id, created_at DESC)`

**Constraints:**
- CHECK: `failure_reason IN ('no_keyword_match', 'external_creation_failed', 'no_board_match')`

---

### 10. processed_emails

Tracks processed emails for duplicate prevention.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Internal identifier |
| inbox_id | INTEGER | NOT NULL, FK → email_inboxes.id ON DELETE CASCADE | Source inbox |
| message_id | VARCHAR(255) | NOT NULL | Email Message-ID header |
| sender_email | VARCHAR(255) | NOT NULL | Sender address |
| subject_hash | VARCHAR(64) | NOT NULL | SHA-256 of normalized subject |
| processed_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Processing time |

**Indexes:**
- `idx_processed_emails_inbox_message` on `(inbox_id, message_id)`
- `idx_processed_emails_duplicate_check` on `(inbox_id, sender_email, subject_hash, processed_at)`

**Constraints:**
- UNIQUE: `(inbox_id, message_id)`

---

## Entity Relationship Diagram

```
                                    ┌─────────────────────┐
                                    │     managers        │
                                    ├─────────────────────┤
                                    │ id (PK)             │
                                    │ email               │
                                    │ password_hash       │
                                    │ name                │
                                    │ timezone            │
                                    │ is_suspended        │
                                    │ suspension_message  │
                                    │ email_verified_at   │
                                    └──────────┬──────────┘
                                               │
              ┌────────────────────────────────┼────────────────────────────────┐
              │                                │                                │
              ▼                                ▼                                ▼
┌─────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│    manager_tokens       │      │     email_inboxes       │      │   standby_queue_items   │
├─────────────────────────┤      ├─────────────────────────┤      ├─────────────────────────┤
│ id (PK)                 │      │ id (PK)                 │      │ id (PK)                 │
│ manager_id (FK)         │      │ manager_id (FK)         │      │ manager_id (FK)         │
│ token_hash              │      │ imap_*/smtp_*           │      │ email_subject/body      │
│ token_type              │      │ polling_interval        │      │ sender_email            │
│ expires_at              │      │ from_address            │      │ failure_reason          │
└─────────────────────────┘      └──────────┬──────────────┘      │ original_board_id (FK)  │
                                            │                      └─────────────────────────┘
                                            │
                         ┌──────────────────┴──────────────────┐
                         │                                     │
                         ▼                                     ▼
           ┌─────────────────────────┐           ┌─────────────────────────┐
           │    processed_emails     │           │        boards           │
           ├─────────────────────────┤           ├─────────────────────────┤
           │ id (PK)                 │           │ id (PK)                 │
           │ inbox_id (FK)           │           │ manager_id (FK)         │
           │ message_id              │           │ name                    │
           │ sender_email            │           │ unique_name             │
           │ subject_hash            │           │ greeting_message        │
           └─────────────────────────┘           │ is_archived             │
                                                 │ external_platform_*     │
                                                 │ exclusive_inbox_id (FK) │
                                                 └──────────┬──────────────┘
                                                            │
                              ┌─────────────────────────────┼─────────────────────────────┐
                              │                             │                             │
                              ▼                             ▼                             ▼
                ┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
                │    board_keywords       │   │        tickets          │   │    external_tickets     │
                ├─────────────────────────┤   ├─────────────────────────┤   ├─────────────────────────┤
                │ id (PK)                 │   │ id (PK)                 │   │ id (PK)                 │
                │ board_id (FK)           │   │ uuid (UNIQUE)           │   │ uuid (UNIQUE)           │
                │ keyword                 │   │ board_id (FK)           │   │ board_id (FK)           │
                └─────────────────────────┘   │ title                   │   │ title                   │
                                              │ description             │   │ creator_email           │
                                              │ state                   │   │ external_url            │
                                              │ creator_email           │   │ external_id             │
                                              │ source                  │   │ platform_type           │
                                              └──────────┬──────────────┘   └─────────────────────────┘
                                                         │
                                                         ▼
                                           ┌─────────────────────────┐
                                           │  ticket_status_changes  │
                                           ├─────────────────────────┤
                                           │ id (PK)                 │
                                           │ ticket_id (FK)          │
                                           │ previous_state          │
                                           │ new_state               │
                                           │ comment                 │
                                           └─────────────────────────┘
```

---

## UUID Uniqueness Across Tables

UUIDs must be unique across both `tickets` and `external_tickets` tables to ensure secret links work correctly.

**Implementation:** Application-level enforcement. On UUID generation, check both tables for conflicts and retry with a new UUID if collision detected. UUID v4 collision probability is astronomically low (~1 in 2^122), making this approach practical and simple.

---

## Encryption Notes

Sensitive fields requiring encryption at rest:
- `email_inboxes.imap_password_encrypted`
- `email_inboxes.smtp_password_encrypted`
- `boards.external_platform_config` (contains API tokens)

Use AES-256-GCM with application-managed encryption key stored in environment variable.

---

## Migration Considerations

1. Create tables in dependency order: managers → manager_tokens, email_inboxes → boards → board_keywords, tickets, external_tickets, etc.
2. Add indexes after initial data load for better performance
3. Consider partial indexes for frequently filtered queries (e.g., active inboxes)

---

## Future Considerations

- Partitioning `tickets` table by `created_at` if volume grows significantly
- Read replicas for dashboard queries
- Archive strategy for old processed_emails records (cleanup job)
