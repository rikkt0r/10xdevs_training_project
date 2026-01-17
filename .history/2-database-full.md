# Database Schema Design Session - Full Transcript

**Date:** 2026-01-17

---

## User

I've provided CLAUDE.md, start taking it into consideration

## Assistant

*Read CLAUDE.md file*

I've read the CLAUDE.md file. It contains project guidelines covering:

- **Frontend**: React (functional components, hooks, memoization, lazy loading) and Redux (RTK, RTK Query, slices, selectors)
- **Coding Practices**: Expert-level support with focus on elegant solutions, performance, and architectural context
- **Version Control**: Conventional commits, feature branches, meaningful commit messages
- **Documentation**: Swagger/OpenAPI best practices
- **Backend**: FastAPI with Pydantic, dependency injection, async endpoints
- **Database**: PostgreSQL with connection pooling, JSONB for flexible data
- **DevOps**: Docker multi-stage builds, GitHub Actions CI/CD
- **Testing**: pytest with fixtures and parameterized tests

I notice some template placeholders remain unfilled (e.g., `{{project-name}}`, `{{project-description}}`). I'll follow these guidelines for all work on this project. What would you like to work on?

---

## User

read the PRD

## Assistant

*Read docs/PRD.md*

I've read the PRD. This is a **Simple Issue Tracker** application with these key characteristics:

**Core Concept:** Managers create ticket boards; users submit tickets via web forms or email; tickets can be managed internally or forwarded to Jira/Trello.

**Tech Stack:**
- Frontend: React (JS), Redux, Bootstrap, Node 22
- Backend: Python 3.12, FastAPI, SQLAlchemy, Alembic
- Database: PostgreSQL
- Deployment: Single Docker container on DigitalOcean
- Logging: GELF format

**User Roles:**
- **Manager**: Authenticated (JWT), creates boards, manages tickets, configures email inboxes and external integrations
- **User**: Unauthenticated, submits tickets via public form or email, views own tickets via secret UUID links

**Key Features:**
- Email inbox configuration with IMAP/SMTP per manager
- Keyword-based email routing to boards
- External platform integration (Jira Cloud, Trello) - one-way only
- Standby queue for unrouted emails and failed external creations
- Ticket states: new → in_progress → closed/rejected
- i18n: English and Polish

**Data Models:** Manager, EmailInbox, Board, BoardKeyword, Ticket, TicketStatusChange, ExternalTicket, StandbyQueueItem

**Out of Scope:** Mobile app, attachments, conversation threads, multi-manager boards, ticket editing/deletion, Jira Server support

What would you like to do with this project?

---

## User

let us create a specification for database. create a schema and then let me review it

## Assistant

I'll create a comprehensive database schema specification based on the PRD. Let me write it to a docs file for your review.

*Created docs/database-schema.md*

I've created the database schema specification at `docs/database-schema.md`. Here's a summary:

**10 Tables:**

| Table | Purpose |
|-------|---------|
| `managers` | User accounts with auth, suspension, timezone |
| `manager_tokens` | JWT refresh, email verification, password reset tokens |
| `email_inboxes` | IMAP/SMTP configuration per manager |
| `boards` | Ticket boards with external platform config (JSONB) |
| `board_keywords` | Keywords for email routing |
| `tickets` | Internal tickets with state machine |
| `ticket_status_changes` | Audit log for state transitions |
| `external_tickets` | References to Jira/Trello tickets |
| `standby_queue_items` | Unrouted emails and failed external creations |
| `processed_emails` | Duplicate email prevention tracking |

**Key Design Decisions:**

1. **Tokens table** instead of separate tables for each token type
2. **JSONB** for external platform config (flexible for Jira vs Trello)
3. **Encrypted fields** for IMAP/SMTP passwords and API tokens (AES-256-GCM)
4. **Application-level UUID uniqueness** across tickets/external_tickets (collision probability negligible)
5. **Partial indexes** for performance on filtered queries
6. **CHECK constraints** for enums (state, token_type, platform_type)

**Added beyond PRD:**
- `source` field on tickets (web vs email)
- `processed_emails` table for duplicate detection
- `retry_count` on standby queue items
- `external_id` on external tickets

Please review and let me know what changes you'd like.

---

## User

annotate in PRD, that key for AES-256-GCM will be stored as env variable

## Assistant

*Read PRD.md section 4.7*

*Edited PRD.md - added ENCRYPTION_KEY to environment variables table*

Added `ENCRYPTION_KEY` to the environment variables table in section 4.7 of the PRD:

```
| ENCRYPTION_KEY | AES-256-GCM key for encrypting sensitive data (IMAP/SMTP passwords, API tokens) |
```

---

## User

update PRD change history

## Assistant

*Read PRD.md document history section*

*Edited PRD.md - added version 0.2*

Done. Added version 0.2 to the document history.

---

## User

how do you fare about index on managers.is_suspended. It will be check rather often

## Assistant

Good question. For `is_suspended`, a standard B-tree index would have poor selectivity (only 2 values, heavily skewed toward FALSE). PostgreSQL would likely ignore it and do a sequential scan anyway.

**However**, there are two scenarios to consider:

1. **Checking suspension during auth/access** - These queries already filter by `id` or `email` (both indexed), so suspension check is just an additional column read on a single row. No index needed.

2. **Bulk operations** (e.g., "skip suspended managers during email polling") - A **partial index** could help:

```sql
CREATE INDEX idx_managers_not_suspended ON managers(id) WHERE is_suspended = FALSE;
```

**My recommendation:** Skip the index for now. The `managers` table will likely remain small (hundreds to low thousands of rows), and most queries already hit the primary key or email index. Add a partial index later if query plans show it's needed.

Want me to add a note about this in the schema doc, or add the partial index preemptively?

---

## User

do nothing on the matter. as to "UUID Uniqueness Across Tables", I choose option A. Modify both PRD and database schema to reflect this choice

## Assistant

*Read PRD.md UUID section*

*Read database-schema.md UUID Uniqueness section*

*Edited database-schema.md - removed options, stated decision directly*

*Edited PRD.md - clarified application-level enforcement*

*Edited PRD.md - added version 0.3 to document history*

Done. Updated both documents:

**PRD (line 416):**
> UUID must be unique across both Ticket and ExternalTicket tables. Enforced at application level: on generation, check both tables for conflicts and retry with new UUID if collision detected.

**Database schema (UUID Uniqueness section):**
Removed options A/B, now states the decision directly with implementation details.

PRD version bumped to 0.3.

---

## User

Now save our conversation into .history/2-database.md

## Assistant

*Created .history/2-database.md*

Done. Saved conversation summary to `.history/2-database.md` covering:
- Tables defined (10 total)
- Key design decisions (encryption, UUID uniqueness, index considerations)
- PRD updates made (v0.2, v0.3)

---

## User

Save our current conversation as whole output to .history/2-database-full.md

## Assistant

*Created this file*
