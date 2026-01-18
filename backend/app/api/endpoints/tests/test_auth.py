"""
Unit tests for authentication endpoints.
"""
import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock

from app.models.manager import Manager
from app.models.manager_token import ManagerToken
from app.core.security import hash_string
from conftest import verify_password


class TestRegister:
    """Tests for POST /api/auth/register"""

    def test_register_success(self, client, mock_email_service, sample_manager_data):
        """Test successful manager registration."""
        response = client.post("/api/auth/register", json=sample_manager_data)

        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert data["data"]["email"] == sample_manager_data["email"]
        assert data["data"]["name"] == sample_manager_data["name"]
        assert data["data"]["email_verified"] is False
        assert data["message"] == "Verification email sent"
        mock_email_service.send_verification_email.assert_called_once()

    def test_register_duplicate_email(self, client, mock_email_service, verified_manager):
        """Test registration with already existing email."""
        response = client.post("/api/auth/register", json={
            "email": verified_manager.email,
            "password": "password123",
            "name": "Another Manager"
        })

        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client, mock_email_service):
        """Test registration with invalid email format."""
        response = client.post("/api/auth/register", json={
            "email": "not-an-email",
            "password": "password123",
            "name": "Test Manager"
        })

        assert response.status_code == 422

    def test_register_short_password(self, client, mock_email_service):
        """Test registration with password shorter than 8 characters."""
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "short",
            "name": "Test Manager"
        })

        assert response.status_code == 422

    def test_register_empty_name(self, client, mock_email_service):
        """Test registration with empty name.

        Note: Current schema allows empty names. This test documents the current behavior.
        If empty names should be rejected, add min_length=1 to RegisterRequest.name.
        """
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": ""
        })

        # Current behavior: empty name is accepted
        assert response.status_code == 201

    def test_register_missing_fields(self, client, mock_email_service):
        """Test registration with missing required fields."""
        response = client.post("/api/auth/register", json={
            "email": "test@example.com"
        })

        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/auth/login"""

    def test_login_success(self, client, verified_manager):
        """Test successful login."""
        response = client.post("/api/auth/login", json={
            "email": verified_manager.email,
            "password": "password123"
        })

        assert response.status_code == 200
        data = response.json()["data"]
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["manager"]["email"] == verified_manager.email
        assert data["manager"]["name"] == verified_manager.name

    def test_login_invalid_email(self, client):
        """Test login with non-existent email."""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })

        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_login_invalid_password(self, client, verified_manager):
        """Test login with wrong password."""
        response = client.post("/api/auth/login", json={
            "email": verified_manager.email,
            "password": "wrongpassword"
        })

        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_login_unverified_email(self, client, unverified_manager):
        """Test login with unverified email."""
        response = client.post("/api/auth/login", json={
            "email": unverified_manager.email,
            "password": "password123"
        })

        assert response.status_code == 403
        assert "not verified" in response.json()["detail"].lower()

    def test_login_suspended_account(self, client, suspended_manager):
        """Test login with suspended account."""
        response = client.post("/api/auth/login", json={
            "email": suspended_manager.email,
            "password": "password123"
        })

        assert response.status_code == 403
        assert "suspended" in response.json()["detail"].lower()

    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format."""
        response = client.post("/api/auth/login", json={
            "email": "not-an-email",
            "password": "password123"
        })

        assert response.status_code == 422


class TestLogout:
    """Tests for POST /api/auth/logout"""

    def test_logout_success(self, client, verified_manager, test_db):
        """Test successful logout."""
        from datetime import timedelta
        from app.core.security import create_access_token
        from app.models.manager import Manager

        # Verify the manager exists in the database
        db_manager = test_db.query(Manager).filter(Manager.id == verified_manager.id).first()
        assert db_manager is not None, f"Manager with id {verified_manager.id} not found in database"

        # Create token for verified manager (created via fixture)
        token = create_access_token(
            data={"sub": verified_manager.id},
            expires_delta=timedelta(hours=24)
        )

        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

    def test_logout_no_token(self, client):
        """Test logout without authentication token."""
        response = client.post("/api/auth/logout")

        assert response.status_code == 403

    def test_logout_invalid_token(self, client):
        """Test logout with invalid token."""
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401


class TestVerifyEmail:
    """Tests for POST /api/auth/verify-email"""

    def test_verify_email_success(self, client, verification_token, test_db, unverified_manager):
        """Test successful email verification."""
        response = client.post("/api/auth/verify-email", json={
            "token": verification_token
        })

        assert response.status_code == 200
        assert "verified successfully" in response.json()["message"].lower()

        # Verify the manager's email is now verified
        test_db.refresh(unverified_manager)
        assert unverified_manager.email_verified_at is not None

    def test_verify_email_invalid_token(self, client):
        """Test email verification with invalid token."""
        response = client.post("/api/auth/verify-email", json={
            "token": "invalid-token"
        })

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    def test_verify_email_expired_token(self, client, expired_verification_token):
        """Test email verification with expired token."""
        response = client.post("/api/auth/verify-email", json={
            "token": expired_verification_token
        })

        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()

    def test_verify_email_already_used_token(self, client, verification_token, test_db):
        """Test email verification with already used token."""
        # First verification should succeed
        response1 = client.post("/api/auth/verify-email", json={
            "token": verification_token
        })
        assert response1.status_code == 200

        # Second verification with same token should fail
        response2 = client.post("/api/auth/verify-email", json={
            "token": verification_token
        })
        assert response2.status_code == 400
        assert "invalid" in response2.json()["detail"].lower() or "used" in response2.json()["detail"].lower()


class TestResendVerification:
    """Tests for POST /api/auth/resend-verification"""

    def test_resend_verification_success(self, client, mock_email_service, unverified_manager):
        """Test successful resend of verification email."""
        response = client.post("/api/auth/resend-verification", json={
            "email": unverified_manager.email
        })

        assert response.status_code == 200
        assert "verification link has been sent" in response.json()["message"].lower()
        mock_email_service.send_verification_email.assert_called_once()

    def test_resend_verification_already_verified(self, client, mock_email_service, verified_manager):
        """Test resend verification for already verified email."""
        response = client.post("/api/auth/resend-verification", json={
            "email": verified_manager.email
        })

        assert response.status_code == 200
        assert "already verified" in response.json()["message"].lower()
        mock_email_service.send_verification_email.assert_not_called()

    def test_resend_verification_nonexistent_email(self, client, mock_email_service):
        """Test resend verification for non-existent email (prevents enumeration)."""
        response = client.post("/api/auth/resend-verification", json={
            "email": "nonexistent@example.com"
        })

        # Should return same message to prevent email enumeration
        assert response.status_code == 200
        assert "verification link has been sent" in response.json()["message"].lower()
        mock_email_service.send_verification_email.assert_not_called()

    def test_resend_verification_invalid_email_format(self, client, mock_email_service):
        """Test resend verification with invalid email format."""
        response = client.post("/api/auth/resend-verification", json={
            "email": "not-an-email"
        })

        assert response.status_code == 422


class TestForgotPassword:
    """Tests for POST /api/auth/forgot-password"""

    def test_forgot_password_success(self, client, mock_email_service, verified_manager):
        """Test successful forgot password request."""
        response = client.post("/api/auth/forgot-password", json={
            "email": verified_manager.email
        })

        assert response.status_code == 200
        assert "reset link has been sent" in response.json()["message"].lower()
        mock_email_service.send_password_reset_email.assert_called_once()

    def test_forgot_password_nonexistent_email(self, client, mock_email_service):
        """Test forgot password for non-existent email (prevents enumeration)."""
        response = client.post("/api/auth/forgot-password", json={
            "email": "nonexistent@example.com"
        })

        # Should return same message to prevent email enumeration
        assert response.status_code == 200
        assert "reset link has been sent" in response.json()["message"].lower()
        mock_email_service.send_password_reset_email.assert_not_called()

    def test_forgot_password_invalid_email_format(self, client, mock_email_service):
        """Test forgot password with invalid email format."""
        response = client.post("/api/auth/forgot-password", json={
            "email": "not-an-email"
        })

        assert response.status_code == 422


class TestResetPassword:
    """Tests for POST /api/auth/reset-password"""

    def test_reset_password_success(self, client, password_reset_token, test_db, verified_manager):
        """Test successful password reset."""
        new_password = "newpassword123"
        old_password_hash = verified_manager.password_hash

        response = client.post("/api/auth/reset-password", json={
            "token": password_reset_token,
            "password": new_password
        })

        assert response.status_code == 200
        assert "reset successfully" in response.json()["message"].lower()

        # Verify the password was actually changed
        test_db.refresh(verified_manager)
        assert verified_manager.password_hash != old_password_hash
        assert verify_password(new_password, verified_manager.password_hash)

    def test_reset_password_invalid_token(self, client):
        """Test password reset with invalid token."""
        response = client.post("/api/auth/reset-password", json={
            "token": "invalid-token",
            "password": "newpassword123"
        })

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    def test_reset_password_expired_token(self, client, expired_password_reset_token):
        """Test password reset with expired token."""
        response = client.post("/api/auth/reset-password", json={
            "token": expired_password_reset_token,
            "password": "newpassword123"
        })

        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()

    def test_reset_password_short_password(self, client, password_reset_token):
        """Test password reset with password shorter than 8 characters."""
        response = client.post("/api/auth/reset-password", json={
            "token": password_reset_token,
            "password": "short"
        })

        assert response.status_code == 422

    def test_reset_password_already_used_token(self, client, password_reset_token):
        """Test password reset with already used token."""
        # First reset should succeed
        response1 = client.post("/api/auth/reset-password", json={
            "token": password_reset_token,
            "password": "newpassword123"
        })
        assert response1.status_code == 200

        # Second reset with same token should fail
        response2 = client.post("/api/auth/reset-password", json={
            "token": password_reset_token,
            "password": "anotherpassword123"
        })
        assert response2.status_code == 400
        assert "invalid" in response2.json()["detail"].lower() or "used" in response2.json()["detail"].lower()


class TestRefreshToken:
    """Tests for POST /api/auth/refresh"""

    def test_refresh_token_success(self, client, verified_manager):
        """Test successful token refresh."""
        from datetime import timedelta
        from app.core.security import create_access_token

        # Create token for verified manager (created via fixture)
        token = create_access_token(
            data={"sub": verified_manager.id},
            expires_delta=timedelta(hours=24)
        )

        response = client.post(
            "/api/auth/refresh",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_refresh_token_no_auth(self, client):
        """Test token refresh without authentication."""
        response = client.post("/api/auth/refresh")

        assert response.status_code == 403

    def test_refresh_token_invalid_token(self, client):
        """Test token refresh with invalid token."""
        response = client.post(
            "/api/auth/refresh",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401

    def test_refresh_token_expired_token(self, client, verified_manager):
        """Test token refresh with expired token."""
        from datetime import timedelta
        from app.core.security import create_access_token

        expired_token = create_access_token(
            data={"sub": verified_manager.id},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )

        response = client.post(
            "/api/auth/refresh",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401


class TestAuthenticationDependency:
    """Tests for authentication dependency behavior."""

    def test_auth_with_unverified_manager_token(self, client, unverified_manager):
        """Test that unverified managers cannot access protected endpoints."""
        from app.core.security import create_access_token
        from datetime import timedelta

        token = create_access_token(
            data={"sub": unverified_manager.id},
            expires_delta=timedelta(hours=24)
        )

        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "not verified" in response.json()["detail"].lower()

    def test_auth_with_suspended_manager_token(self, client, suspended_manager):
        """Test that suspended managers cannot access protected endpoints."""
        from app.core.security import create_access_token
        from datetime import timedelta

        token = create_access_token(
            data={"sub": suspended_manager.id},
            expires_delta=timedelta(hours=24)
        )

        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "suspended" in response.json()["detail"].lower()

    def test_auth_with_nonexistent_manager_id(self, client):
        """Test authentication with token containing non-existent manager ID."""
        from app.core.security import create_access_token
        from datetime import timedelta

        token = create_access_token(
            data={"sub": 99999},  # Non-existent manager ID
            expires_delta=timedelta(hours=24)
        )

        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401
