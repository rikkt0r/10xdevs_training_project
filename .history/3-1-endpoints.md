# Conversation: Enhancing API Endpoint Error Responses

**Date:** 2026-01-17

## Summary

Enhanced the `/api/inboxes/test` and `/api/inboxes/{id}/test` endpoints to return detailed error messages in a simplified format.

---

## Conversation Log

### 1. Initial Request

**User:** read docs/ dir into context

**Assistant:** Read all documentation files from the docs/ directory:
- `docs/PRD.md` - Product Requirements Document
- `docs/database-schema.md` - Database schema specification
- `docs/api-endpoints.md` - API endpoint specification

### 2. First Enhancement Request

**User:** rework "/api/inboxes/test" endpoint to optionally return details of failure

**Assistant:** Enhanced the endpoint with a detailed structured response including:
- Error types (AUTH_FAILED, CONNECTION_TIMEOUT, etc.)
- Nested error objects with `message`, `error_type`, and `details` fields
- Context-specific information in the `details` object
- 7 defined error types with descriptions

Example of initial enhancement:
```json
{
  "data": {
    "imap_status": "failed",
    "imap_error": {
      "message": "Authentication failed",
      "error_type": "AUTH_FAILED",
      "details": {
        "server_response": "Invalid credentials",
        "attempted_username": "support@example.com"
      }
    },
    "smtp_status": "success"
  }
}
```

### 3. Simplification Request

**User:** I changed my mind. Simplify this endpoint. Return only one text field with details, not the whole structure

**Assistant:** Simplified the endpoint to return just a single text field with all details combined in a human-readable format.

---

## Final Implementation

### Response Format

**Success Response (200):**
```json
{
  "data": {
    "imap_status": "success",
    "smtp_status": "success"
  }
}
```

**Failure Response (422) - Single Failure:**
```json
{
  "data": {
    "imap_status": "failed",
    "imap_error": "Authentication failed: Invalid credentials for support@example.com",
    "smtp_status": "success"
  }
}
```

**Failure Response (422) - Multiple Failures:**
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

### Key Features

- Simple text-based error messages
- Includes relevant details (host, port, credentials, timeout values) in human-readable format
- Both IMAP and SMTP tested independently and in parallel
- 10-second timeout per test
- Same format applies to both `/api/inboxes/test` and `/api/inboxes/{id}/test`

---

## Files Modified

- `/home/rikkt0r/projects/10xdevs_training_project/docs/api-endpoints.md`
  - Updated `/api/inboxes/test` endpoint specification
  - Updated `/api/inboxes/{id}/test` endpoint specification
  - Updated document history to version 0.2

---

## Design Decisions

### Why Simplified?

1. **Easier to display:** Single text field is straightforward to show in UI
2. **Less complexity:** No need to parse nested objects on frontend
3. **Human-readable:** Messages are already formatted for end users
4. **Sufficient detail:** All necessary information (host, port, error type) included in the text

### What Details Are Included?

Error messages include contextual information such as:
- Type of failure (authentication, timeout, TLS, etc.)
- Server hostname and port
- Username/credentials used (when relevant)
- Timeout duration (for timeout errors)
- Any specific server responses

---

## Next Steps

When implementing this endpoint in the backend:
1. Test IMAP and SMTP connections in parallel
2. Use 10-second timeout for each connection
3. Format error messages with relevant context
4. Return 200 for success, 422 for connection failures
