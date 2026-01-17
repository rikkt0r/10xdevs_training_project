# Database Schema Design Session

**Date:** 2026-01-17

## Summary

Created comprehensive database schema specification for the Simple Issue Tracker application based on the PRD.

## Artifacts Created

- `docs/database-schema.md` - Full database schema specification

## Tables Defined

1. **managers** - User accounts with auth, suspension, timezone
2. **manager_tokens** - JWT refresh, email verification, password reset tokens
3. **email_inboxes** - IMAP/SMTP configuration per manager
4. **boards** - Ticket boards with external platform config (JSONB)
5. **board_keywords** - Keywords for email routing
6. **tickets** - Internal tickets with state machine
7. **ticket_status_changes** - Audit log for state transitions
8. **external_tickets** - References to Jira/Trello tickets
9. **standby_queue_items** - Unrouted emails and failed external creations
10. **processed_emails** - Duplicate email prevention tracking

## Key Design Decisions

### Encryption
- AES-256-GCM for sensitive data (IMAP/SMTP passwords, API tokens)
- Encryption key stored as environment variable (`ENCRYPTION_KEY`)
- Added to PRD section 4.7

### UUID Uniqueness Across Tables
- **Decision:** Application-level enforcement (Option A)
- On UUID generation, check both `tickets` and `external_tickets` tables for conflicts
- Retry with new UUID if collision detected
- Rationale: UUID v4 collision probability is ~1 in 2^122, making this practical and simple

### Index on managers.is_suspended
- **Decision:** No index needed
- Boolean column with low cardinality and skewed distribution
- Most queries already filter by `id` or `email` (both indexed)
- `managers` table expected to remain small
- Can add partial index later if needed

### Additional Fields Beyond PRD
- `source` field on tickets (web vs email)
- `processed_emails` table for duplicate detection
- `retry_count` on standby queue items
- `external_id` on external tickets

## PRD Updates

- Added `ENCRYPTION_KEY` environment variable (v0.2)
- Clarified UUID uniqueness is enforced at application level (v0.3)
