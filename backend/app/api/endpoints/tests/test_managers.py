"""
Unit tests for manager profile endpoints.
"""
import pytest
from datetime import datetime

from app.models.manager import Manager
from conftest import verify_password


class TestGetProfile:
    """Tests for GET /api/me"""

    def test_get_profile_success(self, client, verified_manager, auth_headers):
        """Test successfully retrieving manager profile."""
        response = client.get("/api/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == verified_manager.id
        assert data["email"] == verified_manager.email
        assert data["name"] == verified_manager.name
        assert data["timezone"] == verified_manager.timezone
        assert data["is_suspended"] is False
        assert "email_verified_at" in data
        assert "created_at" in data

    def test_get_profile_no_auth(self, client):
        """Test retrieving profile without authentication."""
        response = client.get("/api/me")

        assert response.status_code == 403  # FastAPI returns 403 when auth header is missing

    def test_get_profile_invalid_token(self, client):
        """Test retrieving profile with invalid token."""
        response = client.get("/api/me", headers={"Authorization": "Bearer invalid-token"})

        assert response.status_code == 401

    def test_get_profile_suspended_account(self, client, suspended_manager):
        """Test retrieving profile with suspended account.

        Note: Suspended accounts should still be blocked by get_current_manager dependency.
        """
        from app.core.security import create_access_token
        from datetime import timedelta

        token = create_access_token(
            data={"sub": suspended_manager.id},
            expires_delta=timedelta(hours=24)
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/me", headers=headers)

        assert response.status_code == 403
        assert "suspended" in response.json()["detail"].lower()


class TestUpdateProfile:
    """Tests for PATCH /api/me"""

    def test_update_profile_name_only(self, client, verified_manager, auth_headers, test_db):
        """Test updating only the manager name."""
        response = client.patch("/api/me", headers=auth_headers, json={
            "name": "Updated Name"
        })

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Updated Name"
        assert data["timezone"] == verified_manager.timezone  # Unchanged

        # Verify database was updated
        test_db.refresh(verified_manager)
        assert verified_manager.name == "Updated Name"

    def test_update_profile_timezone_only(self, client, verified_manager, auth_headers, test_db):
        """Test updating only the timezone."""
        response = client.patch("/api/me", headers=auth_headers, json={
            "timezone": "America/New_York"
        })

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["timezone"] == "America/New_York"
        assert data["name"] == verified_manager.name  # Unchanged

        # Verify database was updated
        test_db.refresh(verified_manager)
        assert verified_manager.timezone == "America/New_York"

    def test_update_profile_both_fields(self, client, verified_manager, auth_headers, test_db):
        """Test updating both name and timezone."""
        response = client.patch("/api/me", headers=auth_headers, json={
            "name": "New Name",
            "timezone": "Europe/Warsaw"
        })

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "New Name"
        assert data["timezone"] == "Europe/Warsaw"

        # Verify database was updated
        test_db.refresh(verified_manager)
        assert verified_manager.name == "New Name"
        assert verified_manager.timezone == "Europe/Warsaw"

    def test_update_profile_empty_request(self, client, verified_manager, auth_headers, test_db):
        """Test updating profile with empty request (no changes)."""
        original_name = verified_manager.name
        original_timezone = verified_manager.timezone

        response = client.patch("/api/me", headers=auth_headers, json={})

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == original_name
        assert data["timezone"] == original_timezone

    def test_update_profile_no_auth(self, client):
        """Test updating profile without authentication."""
        response = client.patch("/api/me", json={
            "name": "New Name"
        })

        assert response.status_code == 403

    def test_update_profile_name_too_long(self, client, verified_manager, auth_headers):
        """Test updating profile with name exceeding max length."""
        response = client.patch("/api/me", headers=auth_headers, json={
            "name": "x" * 256  # Max is 255
        })

        assert response.status_code == 422


class TestChangePassword:
    """Tests for PUT /api/me/password"""

    def test_change_password_success(self, client, verified_manager, auth_headers, test_db):
        """Test successfully changing password."""
        response = client.put("/api/me/password", headers=auth_headers, json={
            "current_password": "password123",
            "new_password": "newpassword456"
        })

        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"

        # Verify password was changed in database
        test_db.refresh(verified_manager)
        assert verify_password("newpassword456", verified_manager.password_hash)
        assert not verify_password("password123", verified_manager.password_hash)

    def test_change_password_wrong_current(self, client, verified_manager, auth_headers, test_db):
        """Test changing password with incorrect current password."""
        original_hash = verified_manager.password_hash

        response = client.put("/api/me/password", headers=auth_headers, json={
            "current_password": "wrongpassword",
            "new_password": "newpassword456"
        })

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

        # Verify password was not changed
        test_db.refresh(verified_manager)
        assert verified_manager.password_hash == original_hash

    def test_change_password_short_new_password(self, client, verified_manager, auth_headers):
        """Test changing password with new password shorter than 8 characters."""
        response = client.put("/api/me/password", headers=auth_headers, json={
            "current_password": "password123",
            "new_password": "short"
        })

        assert response.status_code == 422

    def test_change_password_no_auth(self, client):
        """Test changing password without authentication."""
        response = client.put("/api/me/password", json={
            "current_password": "password123",
            "new_password": "newpassword456"
        })

        assert response.status_code == 403

    def test_change_password_missing_fields(self, client, verified_manager, auth_headers):
        """Test changing password with missing required fields."""
        response = client.put("/api/me/password", headers=auth_headers, json={
            "current_password": "password123"
        })

        assert response.status_code == 422


class TestSuspendAccount:
    """Tests for POST /api/me/suspend"""

    def test_suspend_account_success(self, client, verified_manager, auth_headers, test_db):
        """Test successfully suspending account."""
        response = client.post("/api/me/suspend", headers=auth_headers, json={
            "suspension_message": "Service no longer available",
            "password": "password123"
        })

        assert response.status_code == 200
        assert response.json()["message"] == "Account suspended successfully"

        # Verify account was suspended in database
        test_db.refresh(verified_manager)
        assert verified_manager.is_suspended is True
        assert verified_manager.suspension_message == "Service no longer available"

    def test_suspend_account_wrong_password(self, client, verified_manager, auth_headers, test_db):
        """Test suspending account with incorrect password."""
        response = client.post("/api/me/suspend", headers=auth_headers, json={
            "suspension_message": "Service no longer available",
            "password": "wrongpassword"
        })

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

        # Verify account was not suspended
        test_db.refresh(verified_manager)
        assert verified_manager.is_suspended is False

    def test_suspend_account_already_suspended(self, client, suspended_manager):
        """Test suspending an already suspended account.

        Note: The dependency get_current_manager blocks suspended accounts,
        so this test will fail at the authentication level.
        """
        from app.core.security import create_access_token
        from datetime import timedelta

        token = create_access_token(
            data={"sub": suspended_manager.id},
            expires_delta=timedelta(hours=24)
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post("/api/me/suspend", headers=headers, json={
            "suspension_message": "Another message",
            "password": "password123"
        })

        # Account is blocked by dependency, not service
        assert response.status_code == 403
        assert "suspended" in response.json()["detail"].lower()

    def test_suspend_account_empty_message(self, client, verified_manager, auth_headers):
        """Test suspending account with empty suspension message."""
        response = client.post("/api/me/suspend", headers=auth_headers, json={
            "suspension_message": "",
            "password": "password123"
        })

        assert response.status_code == 422

    def test_suspend_account_no_auth(self, client):
        """Test suspending account without authentication."""
        response = client.post("/api/me/suspend", json={
            "suspension_message": "Service no longer available",
            "password": "password123"
        })

        assert response.status_code == 403

    def test_suspend_account_missing_fields(self, client, verified_manager, auth_headers):
        """Test suspending account with missing required fields."""
        response = client.post("/api/me/suspend", headers=auth_headers, json={
            "suspension_message": "Service no longer available"
        })

        assert response.status_code == 422
