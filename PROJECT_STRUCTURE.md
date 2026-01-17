# Project Structure

This document describes the file and directory structure of the Simple Issue Tracker project.

## Root Level

```
.
├── .github/                    # GitHub specific files
│   └── workflows/             # GitHub Actions CI/CD workflows
├── .history/                  # Conversation and design history
├── backend/                   # Python FastAPI backend
├── docs/                      # Project documentation
├── frontend/                  # React frontend application
├── scripts/                   # Utility scripts
├── .gitignore                # Git ignore rules
├── .nvmrc                    # Node.js version specification
├── CLAUDE.md                 # AI assistant instructions
├── docker-compose.yml        # Docker Compose for development
├── Dockerfile                # Production Docker image
├── Dockerfile.dev            # Development Docker image
├── PROJECT_STRUCTURE.md      # This file
└── README.md                 # Project overview and setup
```

## Backend Structure

```
backend/
├── alembic/                  # Database migrations
│   ├── versions/            # Migration files
│   ├── env.py              # Alembic environment config
│   └── script.py.mako      # Migration template
├── app/                     # Main application package
│   ├── api/                # API layer
│   │   └── endpoints/      # API endpoint modules
│   ├── core/               # Core functionality
│   │   ├── config.py      # Application settings
│   │   ├── database.py    # Database connection
│   │   └── security.py    # Security utilities
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   │   ├── email/         # Email service (IMAP/SMTP)
│   │   └── external_platforms/  # Jira/Trello integration
│   └── tests/              # Test suite
│       ├── unit/          # Unit tests
│       └── integration/   # Integration tests
├── .env.example            # Environment variables template
├── alembic.ini.example     # Alembic config template
├── pytest.ini              # Pytest configuration
├── pyproject.toml          # Python project config (ruff, etc.)
└── requirements.txt        # Python dependencies
```

## Frontend Structure

```
frontend/
├── public/                  # Static files
│   ├── index.html          # HTML template
│   └── manifest.json       # PWA manifest
├── src/                    # Source code
│   ├── components/         # React components
│   │   ├── common/        # Shared components
│   │   ├── auth/          # Authentication components
│   │   ├── boards/        # Board management components
│   │   ├── tickets/       # Ticket components
│   │   ├── inbox/         # Email inbox components
│   │   └── dashboard/     # Dashboard components
│   ├── pages/             # Page components (routes)
│   ├── store/             # Redux store
│   │   └── slices/        # Redux slices
│   ├── services/          # API services
│   │   └── api.js         # Axios instance and interceptors
│   ├── hooks/             # Custom React hooks
│   ├── utils/             # Utility functions
│   ├── locales/           # Internationalization
│   │   ├── en.json        # English translations
│   │   └── pl.json        # Polish translations
│   ├── styles/            # Global styles
│   ├── tests/             # Frontend tests
│   ├── App.js             # Main App component
│   ├── App.css            # App styles
│   ├── index.js           # React entry point
│   ├── index.css          # Global styles
│   ├── i18n.js            # i18n configuration
│   └── setupTests.js      # Test configuration
├── .env.example           # Environment variables template
├── .prettierrc            # Prettier configuration
└── package.json           # NPM dependencies and scripts
```

## Key Files

### Backend

- **app/main.py**: FastAPI application entry point
- **app/core/config.py**: Application configuration using Pydantic
- **app/core/database.py**: Database connection and session management
- **app/core/security.py**: Authentication, encryption, and password hashing
- **requirements.txt**: Python package dependencies

### Frontend

- **src/index.js**: React application entry point
- **src/App.js**: Main application component with routing
- **src/store/index.js**: Redux store configuration
- **src/services/api.js**: Axios HTTP client with interceptors
- **src/i18n.js**: i18next configuration for English/Polish
- **package.json**: Node.js dependencies and build scripts

### Docker

- **Dockerfile**: Multi-stage production build (frontend + backend)
- **Dockerfile.dev**: Development backend container
- **docker-compose.yml**: Development environment with PostgreSQL

### CI/CD

- **.github/workflows/ci.yml**: GitHub Actions workflow for testing and linting

## Development Workflow

1. **Setup**: Run `scripts/setup.sh` to initialize the development environment
2. **Database**: Use Alembic for database migrations
3. **Testing**: Run `scripts/test.sh` to execute all tests
4. **Backend Development**: `cd backend && uvicorn app.main:app --reload`
5. **Frontend Development**: `cd frontend && npm start`
6. **Docker Development**: `docker-compose up`

## Testing

- **Backend**: pytest with coverage
- **Frontend**: Jest + React Testing Library
- **CI**: Automated via GitHub Actions

## Deployment

Production deployment uses a single Docker container that:
1. Builds the React frontend
2. Serves static files from FastAPI
3. Runs the FastAPI backend with uvicorn
