"""
Unit tests for health check endpoint.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError


@pytest.mark.unit
def test_health_check_healthy(client):
    """Test health check endpoint returns 200 when all systems are healthy."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "details" not in data

    # Verify timestamp is in ISO 8601 format
    timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
    assert timestamp.tzinfo is not None


@pytest.mark.unit
def test_health_check_timestamp_format(client):
    """Test health check endpoint returns properly formatted timestamp."""
    response = client.get("/health")
    data = response.json()

    timestamp_str = data["timestamp"]
    # Should end with 'Z' indicating UTC
    assert timestamp_str.endswith('Z')

    # Should be parseable as ISO 8601
    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    assert isinstance(timestamp, datetime)


@pytest.mark.unit
def test_health_check_no_rate_limiting(client):
    """Test health check endpoint can be called multiple times without rate limiting."""
    # Make multiple requests in quick succession
    for _ in range(10):
        response = client.get("/health")
        assert response.status_code == 200


@pytest.mark.unit
@patch('app.api.endpoints.health.engine')
def test_health_check_unhealthy_database(mock_engine, client):
    """Test health check endpoint returns 503 when database is unhealthy."""
    # Mock database connection failure
    mock_connection = MagicMock()
    mock_connection.execute.side_effect = OperationalError(
        "Connection refused", None, None
    )
    mock_engine.connect.return_value.__enter__.return_value = mock_connection

    response = client.get("/health")
    assert response.status_code == 503

    data = response.json()
    assert data["status"] == "unhealthy"
    assert "timestamp" in data
    assert "details" in data

    # Verify database details are included
    assert "database" in data["details"]
    assert data["details"]["database"]["status"] == "unhealthy"
    assert data["details"]["database"]["message"] is not None


@pytest.mark.unit
@patch('app.api.endpoints.health.engine')
def test_health_check_unhealthy_includes_error_message(mock_engine, client):
    """Test health check endpoint includes error message in details when unhealthy."""
    error_message = "Connection to database failed"

    mock_connection = MagicMock()
    mock_connection.execute.side_effect = OperationalError(
        error_message, None, None
    )
    mock_engine.connect.return_value.__enter__.return_value = mock_connection

    response = client.get("/health")
    data = response.json()

    assert data["status"] == "unhealthy"
    assert error_message in data["details"]["database"]["message"]


@pytest.mark.unit
def test_health_check_response_structure_healthy(client):
    """Test health check response structure when healthy."""
    response = client.get("/health")
    data = response.json()

    # Verify exact structure for healthy response
    assert set(data.keys()) == {"status", "timestamp"}
    assert data["status"] == "healthy"


@pytest.mark.unit
@patch('app.api.endpoints.health.engine')
def test_health_check_response_structure_unhealthy(mock_engine, client):
    """Test health check response structure when unhealthy."""
    mock_connection = MagicMock()
    mock_connection.execute.side_effect = OperationalError(
        "Database error", None, None
    )
    mock_engine.connect.return_value.__enter__.return_value = mock_connection

    response = client.get("/health")
    data = response.json()

    # Verify exact structure for unhealthy response
    assert set(data.keys()) == {"status", "timestamp", "details"}
    assert data["status"] == "unhealthy"
    assert "database" in data["details"]
    assert set(data["details"]["database"].keys()) == {"status", "message"}
