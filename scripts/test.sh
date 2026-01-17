#!/bin/bash

# Test script for running all tests

set -e

echo "Running all tests..."

# Backend tests
echo "Running backend tests..."
cd backend
source venv/bin/activate 2>/dev/null || true
pytest
cd ..

# Frontend tests
echo "Running frontend tests..."
cd frontend
npm test -- --coverage --watchAll=false
cd ..

echo ""
echo "All tests passed!"
