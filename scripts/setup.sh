#!/bin/bash

# Setup script for Simple Issue Tracker development environment

set -e

echo "Setting up Simple Issue Tracker development environment..."

# Check for Python 3.12
echo "Checking Python version..."
python3 --version | grep -E "3.12|3.13" || {
    echo "Error: Python 3.12 or 3.13 is required"
    exit 1
}

# Check for Node.js 22
echo "Checking Node.js version..."
node --version | grep "v22" || {
    echo "Error: Node.js 22 is required"
    exit 1
}

# Setup backend
echo "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit backend/.env with your configuration"
fi

cd ..

# Setup frontend
echo "Setting up frontend..."
cd frontend

echo "Installing frontend dependencies..."
npm install

if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file from example..."
    cp .env.example .env.local
fi

cd ..

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your database and other settings"
echo "2. Start PostgreSQL database"
echo "3. Run database migrations: cd backend && source venv/bin/activate && alembic upgrade head"
echo "4. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "5. Start frontend: cd frontend && npm start"
echo ""
echo "Or use Docker Compose: docker-compose up"
