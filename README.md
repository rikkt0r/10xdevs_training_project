# Simple Issue Tracker

A web application that enables managers to create ticket boards for collecting and tracking issues from users.

## Tech Stack

### Backend
- **Python 3.12**
- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **PostgreSQL** - Database

### Frontend
- **React** (JavaScript)
- **Redux** - State management
- **Bootstrap** - UI framework
- **Node 22**

### Deployment
- **Docker** - Single-container deployment
- **DigitalOcean** - Hosting platform

## Project Structure

```
.
├── backend/                 # FastAPI backend application
│   ├── alembic/            # Database migrations
│   └── app/
│       ├── api/            # API endpoints
│       ├── core/           # Core configuration
│       ├── models/         # SQLAlchemy models
│       ├── schemas/        # Pydantic schemas
│       ├── services/       # Business logic
│       └── tests/          # Backend tests
├── frontend/               # React frontend application
│   ├── public/            # Static assets
│   └── src/
│       ├── components/    # React components
│       ├── pages/         # Page components
│       ├── store/         # Redux store
│       ├── services/      # API services
│       ├── locales/       # i18n translations
│       └── tests/         # Frontend tests
├── docs/                  # Project documentation
├── scripts/               # Utility scripts
└── .github/workflows/     # CI/CD workflows
```

## Features

- **Manager Portal**: Create and manage ticket boards
- **Public Ticket Forms**: Users can submit tickets via web forms
- **Email Integration**: Create tickets via email (IMAP/SMTP)
- **External Platform Integration**: Forward tickets to Jira or Trello
- **Standby Queue**: Manage unrouted tickets
- **Multi-language Support**: English and Polish

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 22+
- PostgreSQL
- Docker (for containerized deployment)

### Development Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Configure your .env file
alembic upgrade head
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Configure your .env.local file
npm start
```

### Docker Deployment

```bash
docker-compose up --build
```

## Documentation

- [Product Requirements Document](docs/PRD.md)
- [Database Schema](docs/database-schema.md)
- [API Endpoints](docs/api-endpoints.md)

## License

Proprietary

## Support

For issues and questions, please contact the development team.
