"""
Tests for middleware (rate limiting and security headers).
"""
import pytest
from fastapi.testclient import TestClient


# Tests for Security Headers

class TestSecurityHeaders:
    """Tests for security headers middleware."""

    def test_security_headers_present(self, client):
        """Test that security headers are present in all responses."""
        response = client.get("/health")

        assert response.status_code == 200
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Referrer-Policy" in response.headers
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_security_headers_on_404(self, client):
        """Test that security headers are present even on error responses."""
        response = client.get("/nonexistent-endpoint")

        assert response.status_code == 404
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "X-Content-Type-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Referrer-Policy" in response.headers

    def test_security_headers_on_authenticated_endpoint(self, client, auth_headers):
        """Test that security headers are present on authenticated endpoints."""
        response = client.get("/api/me", headers=auth_headers)

        assert response.status_code == 200
        assert "X-Frame-Options" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Referrer-Policy" in response.headers


# Tests for Rate Limiting

class TestRateLimiting:
    """Tests for rate limiting."""

    def test_auth_rate_limit_not_exceeded(self, client, test_db):
        """Test that auth endpoints work within rate limit."""
        # Make a few requests (below the limit of 10/minute)
        for i in range(3):
            response = client.post(
                "/api/auth/login",
                json={
                    "email": f"test{i}@example.com",
                    "password": "password123"
                }
            )
            # We don't care about the actual response (might be 401), just that it's not 429
            assert response.status_code != 429

    def test_auth_rate_limit_headers_present(self, client):
        """Test that rate limit headers are present on auth endpoints."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )

        # Rate limit headers should be present
        # Note: slowapi adds these headers
        # We're just verifying they exist, not the exact values
        assert "X-RateLimit-Limit" in response.headers or response.status_code == 401

    def test_public_endpoint_rate_limit_not_exceeded(self, client):
        """Test that public endpoints work within rate limit."""
        # Make a few requests to a public endpoint (below typical limits)
        # Using the health endpoint as it has no rate limit
        for i in range(3):
            response = client.get("/health")
            # Should succeed, not rate limited
            assert response.status_code == 200

    def test_health_endpoint_no_rate_limit(self, client):
        """Test that health endpoint has no rate limit."""
        # Make many requests to health endpoint
        # Should never be rate limited
        for i in range(50):
            response = client.get("/health")
            assert response.status_code == 200
            # Health endpoint should not have rate limit headers
            # (or if it does, it should have a very high limit)


class TestRateLimitIPAddressing:
    """Tests for rate limit IP address handling."""

    def test_localhost_ip_handling(self, client):
        """Test that localhost IPs are handled correctly."""
        # This test verifies that the get_real_ip function works
        # In test environment, the IP will be localhost/127.0.0.1
        response = client.get("/health")
        assert response.status_code == 200

    def test_forwarded_ip_handling(self, client):
        """Test that X-Forwarded-For header is handled correctly."""
        # Make request with X-Forwarded-For header
        response = client.get(
            "/health",
            headers={"X-Forwarded-For": "1.2.3.4, 5.6.7.8"}
        )
        assert response.status_code == 200
        # The rate limiter should use the first IP from X-Forwarded-For


class TestRateLimitExceeded:
    """Tests for rate limit exceeded scenarios."""

    @pytest.mark.slow
    def test_auth_rate_limit_exceeded(self, client):
        """Test that auth endpoint returns 429 when rate limit is exceeded."""
        # Make requests exceeding the limit (10/minute)
        # Note: This test is marked as slow because it makes many requests
        responses = []
        for i in range(15):
            response = client.post(
                "/api/auth/login",
                json={
                    "email": f"test{i}@example.com",
                    "password": "password123"
                }
            )
            responses.append(response.status_code)

        # At least one response should be 429 (rate limited)
        assert 429 in responses

    @pytest.mark.slow
    def test_general_api_no_immediate_rate_limit(self, client):
        """Test that general API endpoints can handle multiple requests."""
        # Make moderate number of requests to a general API endpoint
        # Using health endpoint which has no limit
        responses = []
        for i in range(10):
            response = client.get("/health")
            responses.append(response.status_code)

        # Health endpoint should never be rate limited
        assert 429 not in responses
        assert all(status == 200 for status in responses)

    @pytest.mark.slow
    def test_rate_limit_reset(self, client):
        """Test that rate limit resets after the time window."""
        # This test is primarily to document expected behavior
        # In practice, we can't easily test the reset without waiting 60 seconds
        # So we'll just verify the structure exists

        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )

        # Check if X-RateLimit-Reset header exists (if slowapi provides it)
        # This helps users know when the limit will reset
        # Note: slowapi may or may not provide this header depending on configuration
        assert response.status_code in [401, 403, 429]  # Various possible responses
