# Multi-stage build for production deployment
# Stage 1: Build frontend
FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Build backend with frontend
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend application
COPY backend/ ./backend/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
