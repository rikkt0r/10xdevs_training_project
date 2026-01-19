# Session 8: ORM Classes Implementation and Test Refactoring

## Overview
This session covered implementing all remaining ORM models, creating database migrations, refactoring test structure, adding project-specific coding rules, and fixing authentication test failures.

---

## 1. ORM Models Implementation

### Models Created
Implemented 5 new ORM models to complete the database schema:

1. **BoardKeyword** (`app/models/board_keyword.py`)
   - Keywords for email routing to boards
   - Unique constraint on `(board_id, keyword)`
   - Case-insensitive keyword index

2. **Ticket** (`app/models/ticket.py`)
   - Internal tickets with UUID support
   - States: new, in_progress, closed, rejected
   - Sources: web, email
   - Composite indexes for querying by board and state

3. **TicketStatusChange** (`app/models/ticket_status_change.py`)
   - Audit log for ticket state transitions
   - Enforces state changes (previous ≠ new)
   - Tracks optional comments

4. **ExternalTicket** (`app/models/external_ticket.py`)
   - References to Jira/Trello tickets
   - UUID for public identification
   - Platform types: jira, trello

5. **ProcessedEmail** (`app/models/processed_email.py`)
   - Duplicate email prevention tracking
   - Unique constraint on `(inbox_id, message_id)`
   - Hash-based duplicate detection

### Updated Existing Models
- **Board**: Added relationships to keywords, tickets, and external_tickets
- **EmailInbox**: Added relationship to processed_emails
- **`__init__.py`**: Exported all new models for Alembic

---

## 2. Database Migration

### Migration Creation
- **File**: `alembic/versions/b7375bf8a9b5_add_all_remaining_models.py`
- **Revises**: `1becd249597c`

### Tables Created
1. `email_inboxes` - IMAP/SMTP configuration
2. `boards` - Ticket boards with JSONB config
3. `board_keywords` - Email routing keywords
4. `tickets` - Internal tickets with UUID
5. `ticket_status_changes` - Audit log
6. `external_tickets` - External platform references
7. `standby_queue_items` - Unrouted emails
8. `processed_emails` - Duplicate prevention

### Migration Applied Successfully
```bash
alembic upgrade head
```

All 10 tables verified in database with proper constraints and indexes.

---

## 3. Coding Rules Added to CLAUDE.md

### Backend Project Structure Rules
Added to `BACKEND → Guidelines for PYTHON → PROJECT_STRUCTURE`:

```markdown
- The virtualenv is located at `<project-root>/backend/venv`
- Always change directory to `<project-root>/backend` before running Python code, migrations, or any backend commands
- All configuration files (alembic.ini, etc.) are located in the `<project-root>/backend` directory
- Activate virtualenv using `source venv/bin/activate` from within the backend directory
- Development database is available from project docker-compose. If unable to connect to database, run `docker compose up -d db` from `<project-root>`
- **IMPORTANT**: Always run Alembic migrations and any database-related commands with `dangerouslyDisableSandbox: true` because sandbox mode blocks network connections to localhost
```

### Test Organization Rules
Added to `TESTING → Guidelines for TEST_ORGANIZATION → TEST_STRUCTURE`:

```markdown
- Tests must be organized in `tests/` subdirectories within each module, NOT in a centralized tests directory
- Pattern: `app/module_name/tests/test_*.py` (e.g., `app/services/tests/test_auth_service.py`)
- Each module's `tests/` directory must have an `__init__.py` file
- Shared fixtures and test configuration go in `<project-root>/backend/conftest.py`
- Examples:
  - `app/api/endpoints/auth.py` → `app/api/endpoints/tests/test_auth.py`
  - `app/services/auth_service.py` → `app/services/tests/test_auth_service.py`
  - `app/models/manager.py` → `app/models/tests/test_manager.py`
  - `app/core/security.py` → `app/core/tests/test_security.py`
```

**Rationale**: Sandbox mode blocks network connections, preventing database access during migrations.

---

## 4. Test Structure Refactoring

### Before
```
backend/
└── app/
    └── tests/
        ├── conftest.py
        ├── unit/
        │   ├── test_auth.py
        │   └── test_health.py
        └── integration/
```

### After
```
backend/
├── conftest.py                           # Shared fixtures
└── app/
    ├── api/
    │   ├── endpoints/
    │   │   ├── auth.py
    │   │   └── tests/
    │   │       ├── __init__.py
    │   │       └── test_auth.py          # Auth endpoint tests
    │   └── tests/
    │       ├── __init__.py
    │       └── test_health.py            # Health endpoint tests
    ├── models/
    ├── services/
    └── schemas/
```

### Changes Made
1. Created `tests/` subdirectories in each module
2. Moved `conftest.py` to `backend/` root for shared fixtures
3. Moved `test_auth.py` to `app/api/endpoints/tests/`
4. Moved `test_health.py` to `app/api/tests/`
5. Removed old centralized `app/tests/` directory
6. Updated `pytest.ini` testpaths from `app/tests` to `app`

### Verification
- All 39 tests discovered correctly
- No pytest warnings about missing testpaths

---

## 5. Test Execution and Fixes

### Initial Test Run
- **Result**: 4 failures, 35 passed
- **Coverage**: 92%

### Failed Tests
1. `TestLogout::test_logout_success` - Expected 200, got 401
2. `TestRefreshToken::test_refresh_token_success` - Expected 200, got 401
3. `TestAuthenticationDependency::test_auth_with_unverified_manager_token` - Expected 403, got 401
4. `TestAuthenticationDependency::test_auth_with_suspended_manager_token` - Expected 403, got 401

### Root Cause Analysis
The JWT library (`python-jose`) requires the `sub` (subject) claim to be a **string** per JWT spec, but code was passing **integer** manager IDs, causing token verification to fail silently.

### Fixes Applied

#### Fix 1: `app/core/security.py:28` - `create_access_token()`
```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    # Ensure 'sub' claim is a string (JWT spec requires it)
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt
```

#### Fix 2: `app/api/dependencies.py:45` - `get_current_manager()`
```python
# Get manager ID from payload (convert from string to int)
manager_id_str: Optional[str] = payload.get("sub")
if manager_id_str is None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

try:
    manager_id = int(manager_id_str)
except (ValueError, TypeError):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
```

### Final Test Run
- ✅ **39/39 tests passed** (100% pass rate)
- 📊 **94% code coverage** (up from 92%)
- ⚡ Test execution: 1.07 seconds

---

## Summary

### Completed Tasks
1. ✅ Implemented 5 ORM models (BoardKeyword, Ticket, TicketStatusChange, ExternalTicket, ProcessedEmail)
2. ✅ Updated existing models with relationships
3. ✅ Created and applied database migration
4. ✅ Added project-specific coding rules to CLAUDE.md
5. ✅ Refactored test structure to module-specific `tests/` directories
6. ✅ Fixed JWT authentication issues
7. ✅ All 39 tests passing with 94% coverage

### Key Learnings
- JWT spec requires `sub` claim to be a string
- Sandbox mode blocks localhost network connections
- Tests should be colocated with modules in `tests/` subdirectories
- Database migrations need sandbox disabled for network access

### Files Modified
- `app/models/`: 5 new model files + 2 updated
- `app/models/__init__.py`: Added exports
- `app/core/security.py`: Fixed JWT token creation
- `app/api/dependencies.py`: Fixed JWT token parsing
- `alembic/versions/b7375bf8a9b5_add_all_remaining_models.py`: New migration
- `CLAUDE.md`: Added project structure and test organization rules
- `pytest.ini`: Updated testpaths
- Test files reorganized into module-specific `tests/` directories

### Database State
All 10 tables created and verified:
- managers, manager_tokens, email_inboxes
- boards, board_keywords
- tickets, ticket_status_changes, external_tickets
- standby_queue_items, processed_emails
