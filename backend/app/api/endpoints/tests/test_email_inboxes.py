"""
Unit tests for email inbox endpoints.
"""
import pytest
from app.models.email_inbox import EmailInbox
from app.core.security import encrypt_data


class TestListInboxes:
    """Tests for GET /api/inboxes"""

    def test_list_inboxes_empty(self, client, verified_manager, auth_headers):
        """Test listing inboxes when manager has none."""
        response = client.get("/api/inboxes", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data == []

    def test_list_inboxes_with_data(self, client, verified_manager, auth_headers, test_db):
        """Test listing inboxes with existing data."""
        # Create test inboxes
        inbox1 = EmailInbox(
            manager_id=verified_manager.id,
            name="Test Inbox 1",
            imap_host="imap.test1.com",
            imap_port=993,
            imap_username="user1@test.com",
            imap_password_encrypted=encrypt_data("password1"),
            imap_use_ssl=True,
            smtp_host="smtp.test1.com",
            smtp_port=587,
            smtp_username="user1@test.com",
            smtp_password_encrypted=encrypt_data("password1"),
            smtp_use_tls=True,
            from_address="user1@test.com",
            polling_interval=5
        )
        inbox2 = EmailInbox(
            manager_id=verified_manager.id,
            name="Test Inbox 2",
            imap_host="imap.test2.com",
            imap_port=993,
            imap_username="user2@test.com",
            imap_password_encrypted=encrypt_data("password2"),
            imap_use_ssl=True,
            smtp_host="smtp.test2.com",
            smtp_port=587,
            smtp_username="user2@test.com",
            smtp_password_encrypted=encrypt_data("password2"),
            smtp_use_tls=True,
            from_address="user2@test.com",
            polling_interval=15
        )
        test_db.add_all([inbox1, inbox2])
        test_db.commit()

        response = client.get("/api/inboxes", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2
        assert data[0]["name"] in ["Test Inbox 1", "Test Inbox 2"]
        assert "imap_password_encrypted" not in data[0]  # Passwords not returned

    def test_list_inboxes_no_auth(self, client):
        """Test listing inboxes without authentication."""
        response = client.get("/api/inboxes")

        assert response.status_code == 403


class TestCreateInbox:
    """Tests for POST /api/inboxes"""

    def test_create_inbox_success(self, client, verified_manager, auth_headers, test_db):
        """Test successfully creating an inbox."""
        request_data = {
            "name": "Support Inbox",
            "imap_host": "imap.example.com",
            "imap_port": 993,
            "imap_username": "support@example.com",
            "imap_password": "imapPassword",
            "imap_use_ssl": True,
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "support@example.com",
            "smtp_password": "smtpPassword",
            "smtp_use_tls": True,
            "from_address": "support@example.com",
            "polling_interval": 5
        }

        response = client.post("/api/inboxes", headers=auth_headers, json=request_data)

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "Support Inbox"
        assert data["imap_host"] == "imap.example.com"
        assert data["from_address"] == "support@example.com"
        assert "imap_password" not in data  # Password not returned

        # Verify in database
        inbox = test_db.query(EmailInbox).filter(EmailInbox.name == "Support Inbox").first()
        assert inbox is not None
        assert inbox.manager_id == verified_manager.id

    def test_create_inbox_invalid_polling_interval(self, client, verified_manager, auth_headers):
        """Test creating inbox with invalid polling interval."""
        request_data = {
            "name": "Test Inbox",
            "imap_host": "imap.example.com",
            "imap_port": 993,
            "imap_username": "test@example.com",
            "imap_password": "password",
            "imap_use_ssl": True,
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "test@example.com",
            "smtp_password": "password",
            "smtp_use_tls": True,
            "from_address": "test@example.com",
            "polling_interval": 10  # Invalid - must be 1, 5, or 15
        }

        response = client.post("/api/inboxes", headers=auth_headers, json=request_data)

        assert response.status_code == 422

    def test_create_inbox_no_auth(self, client):
        """Test creating inbox without authentication."""
        request_data = {
            "name": "Test Inbox",
            "imap_host": "imap.example.com",
            "imap_port": 993,
            "imap_username": "test@example.com",
            "imap_password": "password",
            "imap_use_ssl": True,
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "test@example.com",
            "smtp_password": "password",
            "smtp_use_tls": True,
            "from_address": "test@example.com",
            "polling_interval": 5
        }

        response = client.post("/api/inboxes", json=request_data)

        assert response.status_code == 403


class TestGetInbox:
    """Tests for GET /api/inboxes/{id}"""

    def test_get_inbox_success(self, client, verified_manager, auth_headers, test_db):
        """Test getting a specific inbox."""
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Test Inbox",
            imap_host="imap.test.com",
            imap_port=993,
            imap_username="user@test.com",
            imap_password_encrypted=encrypt_data("password"),
            imap_use_ssl=True,
            smtp_host="smtp.test.com",
            smtp_port=587,
            smtp_username="user@test.com",
            smtp_password_encrypted=encrypt_data("password"),
            smtp_use_tls=True,
            from_address="user@test.com",
            polling_interval=5
        )
        test_db.add(inbox)
        test_db.commit()
        test_db.refresh(inbox)

        response = client.get(f"/api/inboxes/{inbox.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == inbox.id
        assert data["name"] == "Test Inbox"

    def test_get_inbox_not_found(self, client, verified_manager, auth_headers):
        """Test getting non-existent inbox."""
        response = client.get("/api/inboxes/9999", headers=auth_headers)

        assert response.status_code == 404

    def test_get_inbox_not_owned(self, client, verified_manager, other_manager, auth_headers, test_db):
        """Test getting inbox owned by another manager."""
        # Create inbox for other manager
        inbox = EmailInbox(
            manager_id=other_manager.id,
            name="Other's Inbox",
            imap_host="imap.test.com",
            imap_port=993,
            imap_username="other@test.com",
            imap_password_encrypted=encrypt_data("password"),
            imap_use_ssl=True,
            smtp_host="smtp.test.com",
            smtp_port=587,
            smtp_username="other@test.com",
            smtp_password_encrypted=encrypt_data("password"),
            smtp_use_tls=True,
            from_address="other@test.com",
            polling_interval=5
        )
        test_db.add(inbox)
        test_db.commit()
        test_db.refresh(inbox)

        response = client.get(f"/api/inboxes/{inbox.id}", headers=auth_headers)

        assert response.status_code == 403


class TestUpdateInbox:
    """Tests for PUT /api/inboxes/{id}"""

    def test_update_inbox_name(self, client, verified_manager, auth_headers, test_db):
        """Test updating inbox name."""
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Original Name",
            imap_host="imap.test.com",
            imap_port=993,
            imap_username="user@test.com",
            imap_password_encrypted=encrypt_data("password"),
            imap_use_ssl=True,
            smtp_host="smtp.test.com",
            smtp_port=587,
            smtp_username="user@test.com",
            smtp_password_encrypted=encrypt_data("password"),
            smtp_use_tls=True,
            from_address="user@test.com",
            polling_interval=5
        )
        test_db.add(inbox)
        test_db.commit()
        test_db.refresh(inbox)

        response = client.put(
            f"/api/inboxes/{inbox.id}",
            headers=auth_headers,
            json={"name": "Updated Name"}
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Updated Name"

        # Verify in database
        test_db.refresh(inbox)
        assert inbox.name == "Updated Name"

    def test_update_inbox_password(self, client, verified_manager, auth_headers, test_db):
        """Test updating inbox password."""
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Test Inbox",
            imap_host="imap.test.com",
            imap_port=993,
            imap_username="user@test.com",
            imap_password_encrypted=encrypt_data("oldpassword"),
            imap_use_ssl=True,
            smtp_host="smtp.test.com",
            smtp_port=587,
            smtp_username="user@test.com",
            smtp_password_encrypted=encrypt_data("oldpassword"),
            smtp_use_tls=True,
            from_address="user@test.com",
            polling_interval=5
        )
        test_db.add(inbox)
        test_db.commit()
        test_db.refresh(inbox)

        old_password_hash = inbox.imap_password_encrypted

        response = client.put(
            f"/api/inboxes/{inbox.id}",
            headers=auth_headers,
            json={"imap_password": "newpassword"}
        )

        assert response.status_code == 200

        # Verify password was re-encrypted
        test_db.refresh(inbox)
        assert inbox.imap_password_encrypted != old_password_hash

    def test_update_inbox_not_owned(self, client, verified_manager, other_manager, auth_headers, test_db):
        """Test updating inbox owned by another manager."""
        inbox = EmailInbox(
            manager_id=other_manager.id,
            name="Other's Inbox",
            imap_host="imap.test.com",
            imap_port=993,
            imap_username="other@test.com",
            imap_password_encrypted=encrypt_data("password"),
            imap_use_ssl=True,
            smtp_host="smtp.test.com",
            smtp_port=587,
            smtp_username="other@test.com",
            smtp_password_encrypted=encrypt_data("password"),
            smtp_use_tls=True,
            from_address="other@test.com",
            polling_interval=5
        )
        test_db.add(inbox)
        test_db.commit()
        test_db.refresh(inbox)

        response = client.put(
            f"/api/inboxes/{inbox.id}",
            headers=auth_headers,
            json={"name": "Hacked Name"}
        )

        assert response.status_code == 403


class TestDeleteInbox:
    """Tests for DELETE /api/inboxes/{id}"""

    def test_delete_inbox_success(self, client, verified_manager, auth_headers, test_db):
        """Test deleting an inbox."""
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Test Inbox",
            imap_host="imap.test.com",
            imap_port=993,
            imap_username="user@test.com",
            imap_password_encrypted=encrypt_data("password"),
            imap_use_ssl=True,
            smtp_host="smtp.test.com",
            smtp_port=587,
            smtp_username="user@test.com",
            smtp_password_encrypted=encrypt_data("password"),
            smtp_use_tls=True,
            from_address="user@test.com",
            polling_interval=5
        )
        test_db.add(inbox)
        test_db.commit()
        test_db.refresh(inbox)
        inbox_id = inbox.id

        response = client.delete(f"/api/inboxes/{inbox_id}", headers=auth_headers)

        assert response.status_code == 204

        # Verify deleted from database
        inbox = test_db.query(EmailInbox).filter(EmailInbox.id == inbox_id).first()
        assert inbox is None

    def test_delete_inbox_not_found(self, client, verified_manager, auth_headers):
        """Test deleting non-existent inbox."""
        response = client.delete("/api/inboxes/9999", headers=auth_headers)

        assert response.status_code == 404


class TestTestConnection:
    """Tests for POST /api/inboxes/test"""

    def test_test_connection_success(self, client, verified_manager, auth_headers):
        """Test connection testing with valid credentials."""
        request_data = {
            "imap_host": "imap.example.com",
            "imap_port": 993,
            "imap_username": "test@example.com",
            "imap_password": "password",
            "imap_use_ssl": True,
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "test@example.com",
            "smtp_password": "password",
            "smtp_use_tls": True
        }

        response = client.post("/api/inboxes/test", headers=auth_headers, json=request_data)

        assert response.status_code == 200
        data = response.json()["data"]
        assert "imap_status" in data
        assert "smtp_status" in data

    def test_test_connection_no_auth(self, client):
        """Test connection testing without authentication."""
        request_data = {
            "imap_host": "imap.example.com",
            "imap_port": 993,
            "imap_username": "test@example.com",
            "imap_password": "password",
            "imap_use_ssl": True,
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "test@example.com",
            "smtp_password": "password",
            "smtp_use_tls": True
        }

        response = client.post("/api/inboxes/test", json=request_data)

        assert response.status_code == 403


class TestTestInboxConnection:
    """Tests for POST /api/inboxes/{id}/test"""

    def test_test_inbox_connection_success(self, client, verified_manager, auth_headers, test_db):
        """Test connection for existing inbox."""
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Test Inbox",
            imap_host="imap.test.com",
            imap_port=993,
            imap_username="user@test.com",
            imap_password_encrypted=encrypt_data("password"),
            imap_use_ssl=True,
            smtp_host="smtp.test.com",
            smtp_port=587,
            smtp_username="user@test.com",
            smtp_password_encrypted=encrypt_data("password"),
            smtp_use_tls=True,
            from_address="user@test.com",
            polling_interval=5
        )
        test_db.add(inbox)
        test_db.commit()
        test_db.refresh(inbox)

        response = client.post(f"/api/inboxes/{inbox.id}/test", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert "imap_status" in data
        assert "smtp_status" in data

    def test_test_inbox_connection_not_found(self, client, verified_manager, auth_headers):
        """Test connection for non-existent inbox."""
        response = client.post("/api/inboxes/9999/test", headers=auth_headers)

        assert response.status_code == 404
