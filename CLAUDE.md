# AI Rules for Simple Issue Tracker

Description available in docs/PRD.md

## FRONTEND

### Guidelines for REACT

#### REACT_CODING_STANDARDS

- Use functional components with hooks instead of class components
- Implement React.memo() for expensive components that render often with the same props
- Utilize React.lazy() and Suspense for code-splitting and performance optimization
- Use the useCallback hook for event handlers passed to child components to prevent unnecessary re-renders
- Prefer useMemo for expensive calculations to avoid recomputation on every render
- Implement useId() for generating unique IDs for accessibility attributes
- Use the new use hook for data fetching in React 19+ projects
- Leverage Server Components for {{data_fetching_heavy_components}} when using React with Next.js or similar frameworks
- Consider using the new useOptimistic hook for optimistic UI updates in forms
- Use useTransition for non-urgent state updates to keep the UI responsive

#### REDUX

- Use Redux Toolkit (RTK) instead of plain Redux to reduce boilerplate code
- Implement the slice pattern for organizing related state, reducers, and actions
- Use RTK Query for data fetching to eliminate manual loading state management
- Prefer createSelector for memoized selectors to prevent unnecessary recalculations
- Normalize complex state structures using a flat entities approach with IDs as references
- Implement middleware selectively and avoid overusing thunks for simple state updates
- Use the listener middleware for complex side effects instead of thunks where appropriate
- Leverage createEntityAdapter for standardized CRUD operations
- Implement Redux DevTools for debugging in development environments
- Use typed hooks (useAppDispatch, useAppSelector) with TypeScript for type safety

## CODING_PRACTICES

### Guidelines for SUPPORT_LEVEL

#### SUPPORT_EXPERT

- Favor elegant, maintainable solutions over verbose code. Assume understanding of language idioms and design patterns.
- Highlight potential performance implications and optimization opportunities in suggested code.
- Frame solutions within broader architectural contexts and suggest design alternatives when appropriate.
- Focus comments on 'why' not 'what' - assume code readability through well-named functions and variables.
- Proactively address edge cases, race conditions, and security considerations without being prompted.
- When debugging, provide targeted diagnostic approaches rather than shotgun solutions.
- Suggest comprehensive testing strategies rather than just example tests, including considerations for mocking, test organization, and coverage.


### Guidelines for VERSION_CONTROL

#### GIT

- Use conventional commits to create meaningful commit messages
- Use feature branches with descriptive names following {{branch_naming_convention}}
- Write meaningful commit messages that explain why changes were made, not just what
- Keep commits focused on single logical changes to facilitate code review and bisection
- Use interactive rebase to clean up history before merging feature branches
- Leverage git hooks to enforce code quality checks before commits and pushes


### Guidelines for DOCUMENTATION

#### SWAGGER

- Define comprehensive schemas for all request and response objects
- Use semantic versioning in API paths to maintain backward compatibility
- Implement detailed descriptions for endpoints, parameters, and {{domain_specific_concepts}}
- Configure security schemes to document authentication and authorization requirements
- Use tags to group related endpoints by resource or functional area
- Implement examples for all endpoints to facilitate easier integration by consumers

## BACKEND

### Guidelines for PYTHON


#### PYTHON

- use `datetime.now(timezone.utc)` instead of **deprecated** `datetime.utcnow()`

#### PROJECT_STRUCTURE

- The virtualenv is located at `<project-root>/backend/venv`
- Always change directory to `<project-root>/backend` before running Python code, migrations, or any backend commands
- All configuration files (alembic.ini, etc.) are located in the `<project-root>/backend` directory
- Activate virtualenv using `source venv/bin/activate` from within the backend directory
- Development database is available from project docker-compose. If unable to connect to database, run `docker compose up -d db` from `<project-root>`
- **IMPORTANT**: Always run Alembic migrations and any database-related commands with `dangerouslyDisableSandbox: true` because sandbox mode blocks network connections to localhost

#### FASTAPI

- Use Pydantic models for request and response validation with strict type checking and custom validators
- **Use Pydantic serialization instead of manual dictionary construction**: Always use `model_validate()` and `model_dump()` to serialize ORM models to response schemas, rather than manually constructing dictionaries with individual field assignments
- Implement dependency injection for services and database sessions to improve testability and resource management
- Use async endpoints for I/O-bound operations to improve throughput for {{high_load_endpoints}}
- Leverage FastAPI's background tasks for non-critical operations that don't need to block the response
- Implement proper exception handling with HTTPException and custom exception handlers for {{error_scenarios}}
- Use path operation decorators consistently with appropriate HTTP methods (GET for retrieval, POST for creation, etc.)

#### FASTAPI_SERIALIZATION

**Always use Pydantic generic response wrappers instead of manual dictionary construction.**

Available generics (defined in `app/api/responses.py`):
- `DataResponse[T]` - wraps data responses as `{"data": T}`
- `MessageResponse` - simple message responses as `{"message": "..."}`
- `PaginatedDataResponse[T]` - wraps paginated data with metadata as `{"data": T, "pagination": {...}}`

These use Python 3.12+ PEP 695 type parameter syntax (`class DataResponse[DataType](BaseModel)`).

**Key patterns:**

1. **Single object response** - pass ORM model or Pydantic model directly:
```python
@router.get("/me", status_code=status.HTTP_200_OK)
def get_profile(
    current_manager: Manager = Depends(get_current_manager)
) -> DataResponse[ManagerProfileResponse]:
    return DataResponse[ManagerProfileResponse](data=current_manager)
```

2. **List response** - use generic with list type:
```python
@router.get("", status_code=status.HTTP_200_OK)
def list_inboxes(
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[list[EmailInboxResponse]]:
    inboxes = email_inbox_service.get_inboxes(db, current_manager)
    return DataResponse[list[EmailInboxResponse]](data=inboxes)
```

3. **Message-only response**:
```python
@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
) -> MessageResponse:
    auth_service.verify_email_token(db, request.token)
    return MessageResponse(message="Email verified successfully")
```

4. **Response with nested data** - pass dict, let Pydantic convert:
```python
@router.get("/{board_id}", status_code=status.HTTP_200_OK)
def get_board(
    board_id: int,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[BoardWithTicketCountsResponse]:
    board, ticket_counts = board_service.get_board(db, current_manager, board_id)

    # Build dict - Pydantic will handle conversion to BoardWithTicketCountsResponse
    board_dict = {
        'id': board.id,
        'name': board.name,
        'ticket_counts': ticket_counts,  # Dict will be converted to TicketCounts
        'created_at': board.created_at
    }

    return DataResponse[BoardWithTicketCountsResponse](data=board_dict)
```

**CRITICAL: Avoid double conversion - Pydantic handles it automatically**

❌ **Bad (unnecessary double conversion):**
```python
# Don't manually instantiate the response schema!
board_dict = {
    'id': board.id,
    'ticket_counts': TicketCounts(**ticket_counts),  # ❌ Unnecessary
}
response = BoardWithTicketCountsResponse(**board_dict)  # ❌ Unnecessary
return DataResponse[BoardWithTicketCountsResponse](data=response)  # ❌ Double conversion
```

✅ **Good (let Pydantic convert):**
```python
# Just pass the dict - Pydantic converts it automatically
board_dict = {
    'id': board.id,
    'ticket_counts': ticket_counts,  # ✅ Pass dict directly
}
return DataResponse[BoardWithTicketCountsResponse](data=board_dict)  # ✅ Single conversion
```

**Key principle:** When using `DataResponse[T]`, pass raw data (dict or ORM model). Pydantic automatically:
- Validates the data against schema T
- Converts dicts to Pydantic models
- Converts ORM models to Pydantic models (via `from_attributes = True`)
- Converts nested dicts to nested Pydantic models

**Bad (manual dictionary construction):**
```python
@router.get("/me")
def get_profile(current_manager: Manager = Depends(get_current_manager)):
    return {
        "data": {
            "id": current_manager.id,
            "email": current_manager.email,
            "name": current_manager.name,
            # ... many more fields
        }
    }
```

**Benefits:**
- **DRY principle** - no field duplication between ORM models and response dicts
- **Type safety** - both runtime (Pydantic validation) and development time (type hints)
- **Maintainability** - schema changes propagate automatically
- **Consistency** - standardized response structure across all endpoints
- **OpenAPI integration** - FastAPI generates correct schemas automatically

## DATABASE

### Guidelines for SQL

#### POSTGRES

- Use connection pooling to manage database connections efficiently
- Implement JSONB columns for semi-structured data instead of creating many tables for {{flexible_data}}
- Use materialized views for complex, frequently accessed read-only data

## DEVOPS

### Guidelines for CONTAINERIZATION

#### DOCKER

- Use multi-stage builds to create smaller production images
- Implement layer caching strategies to speed up builds for {{dependency_types}}
- Use non-root users in containers for better security


### Guidelines for CI_CD

#### GITHUB_ACTIONS

- Check if `package.json` exists in project root and summarize key scripts
- Check if `.nvmrc` exists in project root
- Check if `.env.example` exists in project root to identify key `env:` variables
- Always use terminal command: `git branch -a | cat` to verify whether we use `main` or `master` branch
- Always use `env:` variables and secrets attached to jobs instead of global workflows
- Always use `npm ci` for Node-based dependency setup
- Extract common steps into composite actions in separate files
- Once you're done, as a final step conduct the following: for each public action always use <tool>"Run Terminal"</tool> to see what is the most up-to-date version (use only major version) - extract tag_name from the response:
- ```bash curl -s https://api.github.com/repos/{owner}/{repo}/releases/latest ```

## TESTING

### Guidelines for TEST_ORGANIZATION

#### TEST_STRUCTURE

- Tests must be organized in `tests/` subdirectories within each module, NOT in a centralized tests directory
- Pattern: `app/module_name/tests/test_*.py` (e.g., `app/services/tests/test_auth_service.py`)
- Each module's `tests/` directory must have an `__init__.py` file
- Shared fixtures and test configuration go in `<project-root>/backend/conftest.py`
- Examples:
  - `app/api/endpoints/auth.py` → `app/api/endpoints/tests/test_auth.py`
  - `app/services/auth_service.py` → `app/services/tests/test_auth_service.py`
  - `app/models/manager.py` → `app/models/tests/test_manager.py`
  - `app/core/security.py` → `app/core/tests/test_security.py`

### Guidelines for UNIT

#### PYTEST

- Use fixtures for test setup and dependency injection
- Implement parameterized tests for testing multiple inputs for {{function_types}}
- Use monkeypatch for mocking dependencies
