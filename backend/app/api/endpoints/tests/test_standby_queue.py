"""
Unit tests for standby queue endpoints.
"""
import pytest
from datetime import datetime, timezone

from app.models.standby_queue_item import StandbyQueueItem
from app.models.board import Board
from app.models.ticket import Ticket


@pytest.fixture
def sample_board(test_db, verified_manager):
    """Create a sample board for testing."""
    board = Board(
        manager_id=verified_manager.id,
        name="Test Board",
        unique_name="test-board",
        greeting_message="Test greeting",
        is_archived=False,
        external_platform_type=None
    )
    test_db.add(board)
    test_db.commit()
    test_db.refresh(board)
    return board


@pytest.fixture
def external_board(test_db, verified_manager):
    """Create a board with external platform configuration."""
    board = Board(
        manager_id=verified_manager.id,
        name="External Board",
        unique_name="external-board",
        greeting_message="External platform board",
        is_archived=False,
        external_platform_type="jira",
        external_platform_config={
            "instance_url": "https://test.atlassian.net",
            "project_key": "TEST",
            "api_token_encrypted": "encrypted-token"
        }
    )
    test_db.add(board)
    test_db.commit()
    test_db.refresh(board)
    return board


@pytest.fixture
def other_manager_board(test_db, other_manager):
    """Create a board belonging to another manager."""
    board = Board(
        manager_id=other_manager.id,
        name="Other Board",
        unique_name="other-board",
        greeting_message="Other manager's board",
        is_archived=False
    )
    test_db.add(board)
    test_db.commit()
    test_db.refresh(board)
    return board


@pytest.fixture
def queue_item_no_match(test_db, verified_manager):
    """Create a queue item with no keyword match."""
    item = StandbyQueueItem(
        manager_id=verified_manager.id,
        email_subject="Help needed",
        email_body="I need help with my account",
        sender_email="user@example.com",
        failure_reason="no_keyword_match",
        original_board_id=None,
        retry_count=0
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    return item


@pytest.fixture
def queue_item_external_failed(test_db, verified_manager, external_board):
    """Create a queue item for failed external creation."""
    item = StandbyQueueItem(
        manager_id=verified_manager.id,
        email_subject="Critical issue",
        email_body="System is down",
        sender_email="admin@example.com",
        failure_reason="external_creation_failed",
        original_board_id=external_board.id,
        retry_count=1
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    return item


@pytest.fixture
def queue_item_no_board(test_db, verified_manager):
    """Create a queue item with no board match."""
    item = StandbyQueueItem(
        manager_id=verified_manager.id,
        email_subject="Random email",
        email_body="This email doesn't match any board",
        sender_email="random@example.com",
        failure_reason="no_board_match",
        original_board_id=None,
        retry_count=0
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    return item


@pytest.fixture
def other_manager_queue_item(test_db, other_manager):
    """Create a queue item belonging to another manager."""
    item = StandbyQueueItem(
        manager_id=other_manager.id,
        email_subject="Other manager's item",
        email_body="This belongs to someone else",
        sender_email="other@example.com",
        failure_reason="no_keyword_match",
        original_board_id=None,
        retry_count=0
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    return item


class TestListQueueItems:
    """Tests for GET /api/standby-queue"""

    def test_list_empty_queue(self, client, auth_headers):
        """Test listing queue when it's empty."""
        response = client.get("/api/standby-queue", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total_items"] == 0
        assert data["pagination"]["total_pages"] == 0
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 25

    def test_list_queue_items(self, client, auth_headers, queue_item_no_match,
                               queue_item_external_failed, queue_item_no_board):
        """Test listing all queue items."""
        response = client.get("/api/standby-queue", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3
        assert data["pagination"]["total_items"] == 3
        assert data["pagination"]["total_pages"] == 1

        # Verify items are sorted by created_at DESC (newest first)
        # All created at nearly same time, so just check they're all present
        subjects = [item["email_subject"] for item in data["data"]]
        assert "Help needed" in subjects
        assert "Critical issue" in subjects
        assert "Random email" in subjects

    def test_list_queue_excludes_other_managers(self, client, auth_headers,
                                                 queue_item_no_match, other_manager_queue_item):
        """Test that list only shows current manager's items."""
        response = client.get("/api/standby-queue", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["email_subject"] == "Help needed"
        assert data["pagination"]["total_items"] == 1

    def test_list_queue_pagination(self, client, auth_headers, test_db, verified_manager):
        """Test pagination of queue items."""
        # Create 30 queue items
        for i in range(30):
            item = StandbyQueueItem(
                manager_id=verified_manager.id,
                email_subject=f"Item {i}",
                email_body=f"Body {i}",
                sender_email=f"user{i}@example.com",
                failure_reason="no_keyword_match",
                retry_count=0
            )
            test_db.add(item)
        test_db.commit()

        # Test first page with default limit (25)
        response = client.get("/api/standby-queue", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 25
        assert data["pagination"]["total_items"] == 30
        assert data["pagination"]["total_pages"] == 2
        assert data["pagination"]["page"] == 1

        # Test second page
        response = client.get("/api/standby-queue?page=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 5
        assert data["pagination"]["page"] == 2

    def test_list_queue_custom_limit(self, client, auth_headers, test_db, verified_manager):
        """Test custom page limit."""
        # Create 15 items
        for i in range(15):
            item = StandbyQueueItem(
                manager_id=verified_manager.id,
                email_subject=f"Item {i}",
                email_body=f"Body {i}",
                sender_email=f"user{i}@example.com",
                failure_reason="no_keyword_match",
                retry_count=0
            )
            test_db.add(item)
        test_db.commit()

        # Request with limit=10
        response = client.get("/api/standby-queue?limit=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 10
        assert data["pagination"]["limit"] == 10
        assert data["pagination"]["total_pages"] == 2

    def test_list_queue_no_auth(self, client):
        """Test listing queue without authentication."""
        response = client.get("/api/standby-queue")
        assert response.status_code == 403

    def test_list_queue_invalid_token(self, client):
        """Test listing queue with invalid token."""
        response = client.get(
            "/api/standby-queue",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401


class TestGetQueueItem:
    """Tests for GET /api/standby-queue/{id}"""

    def test_get_queue_item_success(self, client, auth_headers, queue_item_no_match):
        """Test getting a specific queue item."""
        response = client.get(
            f"/api/standby-queue/{queue_item_no_match.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == queue_item_no_match.id
        assert data["email_subject"] == "Help needed"
        assert data["email_body"] == "I need help with my account"
        assert data["sender_email"] == "user@example.com"
        assert data["failure_reason"] == "no_keyword_match"
        assert data["original_board_id"] is None
        assert data["retry_count"] == 0
        assert "created_at" in data

    def test_get_external_failed_item(self, client, auth_headers, queue_item_external_failed, external_board):
        """Test getting an external creation failure item."""
        response = client.get(
            f"/api/standby-queue/{queue_item_external_failed.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["failure_reason"] == "external_creation_failed"
        assert data["original_board_id"] == external_board.id
        assert data["retry_count"] == 1

    def test_get_nonexistent_item(self, client, auth_headers):
        """Test getting a non-existent queue item."""
        response = client.get("/api/standby-queue/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_other_manager_item(self, client, auth_headers, other_manager_queue_item):
        """Test getting another manager's queue item."""
        response = client.get(
            f"/api/standby-queue/{other_manager_queue_item.id}",
            headers=auth_headers
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_queue_item_no_auth(self, client, queue_item_no_match):
        """Test getting queue item without authentication."""
        response = client.get(f"/api/standby-queue/{queue_item_no_match.id}")
        assert response.status_code == 403


class TestAssignToBoard:
    """Tests for POST /api/standby-queue/{id}/assign"""

    def test_assign_to_board_success(self, client, auth_headers, queue_item_no_match,
                                     sample_board, test_db):
        """Test successfully assigning queue item to board."""
        response = client.post(
            f"/api/standby-queue/{queue_item_no_match.id}/assign",
            headers=auth_headers,
            json={"board_id": sample_board.id}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Ticket created successfully"
        assert "data" in data
        assert "ticket" in data["data"]

        ticket = data["data"]["ticket"]
        assert ticket["title"] == "Help needed"
        assert ticket["board_id"] == sample_board.id
        assert "uuid" in ticket
        assert "id" in ticket

        # Verify ticket was created in database
        created_ticket = test_db.query(Ticket).filter(Ticket.id == ticket["id"]).first()
        assert created_ticket is not None
        assert created_ticket.title == "Help needed"
        assert created_ticket.description == "I need help with my account"
        assert created_ticket.creator_email == "user@example.com"
        assert created_ticket.source == "email"
        assert created_ticket.state == "new"

        # Verify queue item was removed
        queue_item = test_db.query(StandbyQueueItem).filter(
            StandbyQueueItem.id == queue_item_no_match.id
        ).first()
        assert queue_item is None

    def test_assign_to_board_nonexistent_item(self, client, auth_headers, sample_board):
        """Test assigning non-existent queue item."""
        response = client.post(
            "/api/standby-queue/99999/assign",
            headers=auth_headers,
            json={"board_id": sample_board.id}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_assign_to_nonexistent_board(self, client, auth_headers, queue_item_no_match):
        """Test assigning to non-existent board."""
        response = client.post(
            f"/api/standby-queue/{queue_item_no_match.id}/assign",
            headers=auth_headers,
            json={"board_id": 99999}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_assign_to_other_manager_board(self, client, auth_headers, queue_item_no_match,
                                           other_manager_board):
        """Test assigning to another manager's board."""
        response = client.post(
            f"/api/standby-queue/{queue_item_no_match.id}/assign",
            headers=auth_headers,
            json={"board_id": other_manager_board.id}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_assign_other_manager_item(self, client, auth_headers, other_manager_queue_item,
                                       sample_board):
        """Test assigning another manager's queue item."""
        response = client.post(
            f"/api/standby-queue/{other_manager_queue_item.id}/assign",
            headers=auth_headers,
            json={"board_id": sample_board.id}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_assign_invalid_board_id(self, client, auth_headers, queue_item_no_match):
        """Test assigning with invalid board_id."""
        response = client.post(
            f"/api/standby-queue/{queue_item_no_match.id}/assign",
            headers=auth_headers,
            json={"board_id": 0}
        )
        assert response.status_code == 422

    def test_assign_missing_board_id(self, client, auth_headers, queue_item_no_match):
        """Test assigning without board_id."""
        response = client.post(
            f"/api/standby-queue/{queue_item_no_match.id}/assign",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 422

    def test_assign_no_auth(self, client, queue_item_no_match, sample_board):
        """Test assigning without authentication."""
        response = client.post(
            f"/api/standby-queue/{queue_item_no_match.id}/assign",
            json={"board_id": sample_board.id}
        )
        assert response.status_code == 403


class TestRetryExternal:
    """Tests for POST /api/standby-queue/{id}/retry"""

    def test_retry_external_not_implemented(self, client, auth_headers, queue_item_external_failed):
        """Test retry external creation (currently returns not implemented error)."""
        response = client.post(
            f"/api/standby-queue/{queue_item_external_failed.id}/retry",
            headers=auth_headers
        )

        # The service currently returns 422 with "not yet implemented" message
        assert response.status_code == 422
        assert "not yet implemented" in response.json()["detail"].lower()

    def test_retry_wrong_failure_reason(self, client, auth_headers, queue_item_no_match):
        """Test retry on item that's not external_creation_failed."""
        response = client.post(
            f"/api/standby-queue/{queue_item_no_match.id}/retry",
            headers=auth_headers
        )

        assert response.status_code == 422
        assert "only applicable for external creation failures" in response.json()["detail"].lower()

    def test_retry_no_board_match_item(self, client, auth_headers, queue_item_no_board):
        """Test retry on no_board_match item."""
        response = client.post(
            f"/api/standby-queue/{queue_item_no_board.id}/retry",
            headers=auth_headers
        )

        assert response.status_code == 422
        assert "only applicable for external creation failures" in response.json()["detail"].lower()

    def test_retry_nonexistent_item(self, client, auth_headers):
        """Test retry on non-existent item."""
        response = client.post(
            "/api/standby-queue/99999/retry",
            headers=auth_headers
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_retry_other_manager_item(self, client, auth_headers, other_manager_queue_item):
        """Test retry on another manager's item."""
        response = client.post(
            f"/api/standby-queue/{other_manager_queue_item.id}/retry",
            headers=auth_headers
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_retry_no_auth(self, client, queue_item_external_failed):
        """Test retry without authentication."""
        response = client.post(
            f"/api/standby-queue/{queue_item_external_failed.id}/retry"
        )
        assert response.status_code == 403

    def test_retry_increments_count(self, client, auth_headers, queue_item_external_failed, test_db):
        """Test that retry increments retry_count even when it fails."""
        original_retry_count = queue_item_external_failed.retry_count

        response = client.post(
            f"/api/standby-queue/{queue_item_external_failed.id}/retry",
            headers=auth_headers
        )

        # Should fail with 422 but increment count
        assert response.status_code == 422

        # Refresh and check count was incremented
        test_db.refresh(queue_item_external_failed)
        assert queue_item_external_failed.retry_count == original_retry_count + 1


class TestDeleteQueueItem:
    """Tests for DELETE /api/standby-queue/{id}"""

    def test_delete_queue_item_success(self, client, auth_headers, queue_item_no_match, test_db):
        """Test successfully deleting a queue item."""
        item_id = queue_item_no_match.id

        response = client.delete(
            f"/api/standby-queue/{item_id}",
            headers=auth_headers
        )

        assert response.status_code == 204
        assert response.content == b""

        # Verify item was deleted from database
        deleted_item = test_db.query(StandbyQueueItem).filter(
            StandbyQueueItem.id == item_id
        ).first()
        assert deleted_item is None

    def test_delete_external_failed_item(self, client, auth_headers, queue_item_external_failed, test_db):
        """Test deleting an external creation failure item."""
        item_id = queue_item_external_failed.id

        response = client.delete(
            f"/api/standby-queue/{item_id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deletion
        deleted_item = test_db.query(StandbyQueueItem).filter(
            StandbyQueueItem.id == item_id
        ).first()
        assert deleted_item is None

    def test_delete_nonexistent_item(self, client, auth_headers):
        """Test deleting a non-existent queue item."""
        response = client.delete(
            "/api/standby-queue/99999",
            headers=auth_headers
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_other_manager_item(self, client, auth_headers, other_manager_queue_item, test_db):
        """Test deleting another manager's queue item."""
        item_id = other_manager_queue_item.id

        response = client.delete(
            f"/api/standby-queue/{item_id}",
            headers=auth_headers
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

        # Verify item still exists (not deleted)
        still_exists = test_db.query(StandbyQueueItem).filter(
            StandbyQueueItem.id == item_id
        ).first()
        assert still_exists is not None

    def test_delete_no_auth(self, client, queue_item_no_match):
        """Test deleting without authentication."""
        response = client.delete(f"/api/standby-queue/{queue_item_no_match.id}")
        assert response.status_code == 403

    def test_delete_invalid_token(self, client, queue_item_no_match):
        """Test deleting with invalid token."""
        response = client.delete(
            f"/api/standby-queue/{queue_item_no_match.id}",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401


class TestQueueItemValidation:
    """Tests for queue item data validation."""

    def test_queue_item_response_structure(self, client, auth_headers, queue_item_no_match):
        """Test that queue item response has correct structure."""
        response = client.get(
            f"/api/standby-queue/{queue_item_no_match.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()["data"]

        # Verify all required fields are present
        required_fields = [
            "id", "email_subject", "email_body", "sender_email",
            "failure_reason", "original_board_id", "retry_count", "created_at"
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_pagination_response_structure(self, client, auth_headers, queue_item_no_match):
        """Test that pagination response has correct structure."""
        response = client.get("/api/standby-queue", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

        # Verify pagination fields
        pagination = data["pagination"]
        required_pagination_fields = ["page", "limit", "total_items", "total_pages"]
        for field in required_pagination_fields:
            assert field in pagination, f"Missing pagination field: {field}"
