"""
Unit tests for health check endpoint.
"""
import pytest


@pytest.mark.unit
def test_health_check(client):
    """Test health check endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
