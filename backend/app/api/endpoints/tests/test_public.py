"""
Tests for public endpoints (no authentication required).
"""
import pytest
from datetime import datetime, timezone
import uuid

from app.models.board import Board
from app.models.ticket import Ticket
from app.models.external_ticket import ExternalTicket
from app.models.ticket_status_change import TicketStatusChange


# Fixtures

@pytest.fixture
def active_board(test_db, verified_manager):
    """Create an active board for testing."""
    board = Board(
        manager_id=verified_manager.id,
        name="Support Board",
        unique_name="support",
        greeting_message="Welcome! Tell us how we can help.",
        is_archived=False,
        external_platform_type=None
    )
    test_db.add(board)
    test_db.commit()
    test_db.refresh(board)
    return board


@pytest.fixture
def archived_board(test_db, verified_manager):
    """Create an archived board for testing."""
    board = Board(
        manager_id=verified_manager.id,
        name="Archived Board",
        unique_name="archived",
        greeting_message="This board is archived",
        is_archived=True,
        external_platform_type=None
    )
    test_db.add(board)
    test_db.commit()
    test_db.refresh(board)
    return board


@pytest.fixture
def suspended_manager_board(test_db, suspended_manager):
    """Create a board owned by a suspended manager."""
    board = Board(
        manager_id=suspended_manager.id,
        name="Suspended Manager Board",
        unique_name="suspended-board",
        greeting_message="This board should not be accessible",
        is_archived=False,
        external_platform_type=None
    )
    test_db.add(board)
    test_db.commit()
    test_db.refresh(board)
    return board


@pytest.fixture
def sample_ticket(test_db, active_board):
    """Create a sample ticket for viewing tests."""
    ticket = Ticket(
        board_id=active_board.id,
        title="Test Issue",
        description="This is a test issue description",
        creator_email="user@example.com",
        source="web",
        state="new"
    )
    test_db.add(ticket)
    test_db.commit()
    test_db.refresh(ticket)
    return ticket


@pytest.fixture
def ticket_with_status_changes(test_db, active_board):
    """Create a ticket with status changes for viewing tests."""
    ticket = Ticket(
        board_id=active_board.id,
        title="Issue with Status Changes",
        description="This ticket has status changes",
        creator_email="user@example.com",
        source="web",
        state="in_progress"
    )
    test_db.add(ticket)
    test_db.commit()
    test_db.refresh(ticket)

    # Add status changes
    status_change = TicketStatusChange(
        ticket_id=ticket.id,
        previous_state="new",
        new_state="in_progress",
        comment="Working on this issue"
    )
    test_db.add(status_change)
    test_db.commit()

    test_db.refresh(ticket)
    return ticket


@pytest.fixture
def sample_external_ticket(test_db, active_board):
    """Create a sample external ticket for viewing tests."""
    external_ticket = ExternalTicket(
        board_id=active_board.id,
        title="External Issue",
        creator_email="user@example.com",
        external_url="https://jira.example.com/browse/ISSUE-123",
        external_id="ISSUE-123",
        platform_type="jira"
    )
    test_db.add(external_ticket)
    test_db.commit()
    test_db.refresh(external_ticket)
    return external_ticket


# Tests for GET /api/public/boards/{unique_name}

class TestGetBoardInfo:
    """Tests for getting public board information."""

    def test_get_board_info_success(self, client, active_board):
        """Test successful retrieval of board info."""
        response = client.get(f"/api/public/boards/{active_board.unique_name}")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["name"] == "Support Board"
        assert data["data"]["greeting_message"] == "Welcome! Tell us how we can help."

    def test_get_board_info_not_found(self, client):
        """Test board not found."""
        response = client.get("/api/public/boards/nonexistent")

        assert response.status_code == 404

    def test_get_board_info_manager_suspended(self, client, suspended_manager_board):
        """Test board info when manager is suspended."""
        response = client.get(f"/api/public/boards/{suspended_manager_board.unique_name}")

        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "Account suspended for testing" in data["detail"]

    def test_get_board_info_board_archived(self, client, archived_board):
        """Test board info when board is archived."""
        response = client.get(f"/api/public/boards/{archived_board.unique_name}")

        assert response.status_code == 410
        data = response.json()
        assert "detail" in data
        assert "no longer accepting" in data["detail"].lower()

    def test_get_board_info_without_greeting_message(self, test_db, verified_manager, client):
        """Test board info when greeting message is null."""
        board = Board(
            manager_id=verified_manager.id,
            name="Board Without Greeting",
            unique_name="no-greeting",
            greeting_message=None,
            is_archived=False
        )
        test_db.add(board)
        test_db.commit()

        response = client.get("/api/public/boards/no-greeting")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Board Without Greeting"
        assert data["data"]["greeting_message"] is None


# Tests for POST /api/public/boards/{unique_name}/tickets

class TestCreatePublicTicket:
    """Tests for creating tickets via public form."""

    def test_create_ticket_success(self, client, active_board, test_db):
        """Test successful ticket creation."""
        ticket_data = {
            "email": "user@example.com",
            "title": "My issue with login",
            "description": "I cannot log into my account. It keeps saying invalid credentials."
        }

        response = client.post(
            f"/api/public/boards/{active_board.unique_name}/tickets",
            json=ticket_data
        )

        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert "uuid" in data["data"]
        assert data["data"]["title"] == "My issue with login"
        assert "confirmation email" in data["data"]["message"].lower()

        # Verify ticket was created in database
        ticket = test_db.query(Ticket).filter(
            Ticket.title == "My issue with login"
        ).first()
        assert ticket is not None
        assert ticket.creator_email == "user@example.com"
        assert ticket.description == "I cannot log into my account. It keeps saying invalid credentials."
        assert ticket.source == "web"
        assert ticket.state == "new"
        assert ticket.board_id == active_board.id

    def test_create_ticket_board_not_found(self, client):
        """Test ticket creation when board doesn't exist."""
        ticket_data = {
            "email": "user@example.com",
            "title": "Test issue",
            "description": "Test description"
        }

        response = client.post(
            "/api/public/boards/nonexistent/tickets",
            json=ticket_data
        )

        assert response.status_code == 404

    def test_create_ticket_manager_suspended(self, client, suspended_manager_board):
        """Test ticket creation when manager is suspended."""
        ticket_data = {
            "email": "user@example.com",
            "title": "Test issue",
            "description": "Test description"
        }

        response = client.post(
            f"/api/public/boards/{suspended_manager_board.unique_name}/tickets",
            json=ticket_data
        )

        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "Account suspended for testing" in data["detail"]

    def test_create_ticket_board_archived(self, client, archived_board):
        """Test ticket creation when board is archived."""
        ticket_data = {
            "email": "user@example.com",
            "title": "Test issue",
            "description": "Test description"
        }

        response = client.post(
            f"/api/public/boards/{archived_board.unique_name}/tickets",
            json=ticket_data
        )

        assert response.status_code == 410
        data = response.json()
        assert "detail" in data

    def test_create_ticket_invalid_email(self, client, active_board):
        """Test ticket creation with invalid email format."""
        ticket_data = {
            "email": "not-an-email",
            "title": "Test issue",
            "description": "Test description"
        }

        response = client.post(
            f"/api/public/boards/{active_board.unique_name}/tickets",
            json=ticket_data
        )

        assert response.status_code == 422

    def test_create_ticket_title_too_long(self, client, active_board):
        """Test ticket creation with title exceeding max length."""
        ticket_data = {
            "email": "user@example.com",
            "title": "a" * 256,  # Max is 255
            "description": "Test description"
        }

        response = client.post(
            f"/api/public/boards/{active_board.unique_name}/tickets",
            json=ticket_data
        )

        assert response.status_code == 422

    def test_create_ticket_description_too_long(self, client, active_board):
        """Test ticket creation with description exceeding max length."""
        ticket_data = {
            "email": "user@example.com",
            "title": "Test issue",
            "description": "a" * 6001  # Max is 6000
        }

        response = client.post(
            f"/api/public/boards/{active_board.unique_name}/tickets",
            json=ticket_data
        )

        assert response.status_code == 422

    def test_create_ticket_missing_email(self, client, active_board):
        """Test ticket creation without email."""
        ticket_data = {
            "title": "Test issue",
            "description": "Test description"
        }

        response = client.post(
            f"/api/public/boards/{active_board.unique_name}/tickets",
            json=ticket_data
        )

        assert response.status_code == 422

    def test_create_ticket_missing_title(self, client, active_board):
        """Test ticket creation without title."""
        ticket_data = {
            "email": "user@example.com",
            "description": "Test description"
        }

        response = client.post(
            f"/api/public/boards/{active_board.unique_name}/tickets",
            json=ticket_data
        )

        assert response.status_code == 422

    def test_create_ticket_missing_description(self, client, active_board):
        """Test ticket creation without description."""
        ticket_data = {
            "email": "user@example.com",
            "title": "Test issue"
        }

        response = client.post(
            f"/api/public/boards/{active_board.unique_name}/tickets",
            json=ticket_data
        )

        assert response.status_code == 422

    def test_create_ticket_empty_title(self, client, active_board):
        """Test ticket creation with empty title."""
        ticket_data = {
            "email": "user@example.com",
            "title": "   ",  # Whitespace only
            "description": "Test description"
        }

        response = client.post(
            f"/api/public/boards/{active_board.unique_name}/tickets",
            json=ticket_data
        )

        assert response.status_code == 422

    def test_create_ticket_empty_description(self, client, active_board):
        """Test ticket creation with empty description."""
        ticket_data = {
            "email": "user@example.com",
            "title": "Test issue",
            "description": "   "  # Whitespace only
        }

        response = client.post(
            f"/api/public/boards/{active_board.unique_name}/tickets",
            json=ticket_data
        )

        assert response.status_code == 422

    def test_create_ticket_strips_whitespace(self, client, active_board, test_db):
        """Test that title and description whitespace is stripped."""
        ticket_data = {
            "email": "user@example.com",
            "title": "  Test issue  ",
            "description": "  Test description  "
        }

        response = client.post(
            f"/api/public/boards/{active_board.unique_name}/tickets",
            json=ticket_data
        )

        assert response.status_code == 201

        # Verify whitespace was stripped
        ticket = test_db.query(Ticket).filter(
            Ticket.title == "Test issue"
        ).first()
        assert ticket is not None
        assert ticket.title == "Test issue"
        assert ticket.description == "Test description"


# Tests for GET /api/public/tickets/{uuid}

class TestGetPublicTicket:
    """Tests for viewing tickets by UUID."""

    def test_get_internal_ticket_success(self, client, sample_ticket):
        """Test successful retrieval of internal ticket."""
        response = client.get(f"/api/public/tickets/{sample_ticket.uuid}")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["uuid"] == str(sample_ticket.uuid)
        assert data["data"]["title"] == "Test Issue"
        assert data["data"]["description"] == "This is a test issue description"
        assert data["data"]["state"] == "new"
        assert data["data"]["board_name"] == "Support Board"
        assert "created_at" in data["data"]
        assert "updated_at" in data["data"]
        assert "status_changes" in data["data"]
        assert isinstance(data["data"]["status_changes"], list)

    def test_get_internal_ticket_with_status_changes(self, client, ticket_with_status_changes):
        """Test retrieval of internal ticket with status changes."""
        response = client.get(f"/api/public/tickets/{ticket_with_status_changes.uuid}")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["state"] == "in_progress"
        assert len(data["data"]["status_changes"]) == 1
        assert data["data"]["status_changes"][0]["previous_state"] == "new"
        assert data["data"]["status_changes"][0]["new_state"] == "in_progress"
        assert data["data"]["status_changes"][0]["comment"] == "Working on this issue"

    def test_get_external_ticket_success(self, client, sample_external_ticket):
        """Test successful retrieval of external ticket."""
        response = client.get(f"/api/public/tickets/{sample_external_ticket.uuid}")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["uuid"] == str(sample_external_ticket.uuid)
        assert data["data"]["title"] == "External Issue"
        assert data["data"]["board_name"] == "Support Board"
        assert data["data"]["external_url"] == "https://jira.example.com/browse/ISSUE-123"
        assert data["data"]["platform_type"] == "jira"
        assert "created_at" in data["data"]
        # External tickets should not have description, state, or status_changes
        assert "description" not in data["data"]
        assert "state" not in data["data"]
        assert "status_changes" not in data["data"]

    def test_get_ticket_not_found(self, client):
        """Test ticket not found."""
        random_uuid = uuid.uuid4()
        response = client.get(f"/api/public/tickets/{random_uuid}")

        assert response.status_code == 404

    def test_get_ticket_invalid_uuid(self, client):
        """Test invalid UUID format."""
        response = client.get("/api/public/tickets/not-a-valid-uuid")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


# Tests for response structure validation

class TestPublicResponseStructure:
    """Tests for validating response structure matches API spec."""

    def test_board_info_response_structure(self, client, active_board):
        """Test board info response has correct structure."""
        response = client.get(f"/api/public/boards/{active_board.unique_name}")

        assert response.status_code == 200
        data = response.json()

        # Should have 'data' wrapper
        assert "data" in data
        assert set(data.keys()) == {"data"}

        # Data should have name and greeting_message
        board_data = data["data"]
        assert "name" in board_data
        assert "greeting_message" in board_data
        assert isinstance(board_data["name"], str)
        assert isinstance(board_data["greeting_message"], (str, type(None)))

    def test_create_ticket_response_structure(self, client, active_board):
        """Test create ticket response has correct structure."""
        ticket_data = {
            "email": "user@example.com",
            "title": "Structure test",
            "description": "Testing response structure"
        }

        response = client.post(
            f"/api/public/boards/{active_board.unique_name}/tickets",
            json=ticket_data
        )

        assert response.status_code == 201
        data = response.json()

        # Should have 'data' wrapper
        assert "data" in data
        assert set(data.keys()) == {"data"}

        # Data should have uuid, title, message
        ticket_response = data["data"]
        assert "uuid" in ticket_response
        assert "title" in ticket_response
        assert "message" in ticket_response
        assert isinstance(ticket_response["title"], str)
        assert isinstance(ticket_response["message"], str)

    def test_internal_ticket_view_response_structure(self, client, sample_ticket):
        """Test internal ticket view response has correct structure."""
        response = client.get(f"/api/public/tickets/{sample_ticket.uuid}")

        assert response.status_code == 200
        data = response.json()

        # Should have 'data' wrapper
        assert "data" in data

        # Data should have all required fields for internal ticket
        ticket_data = data["data"]
        required_fields = {
            "uuid", "title", "description", "state",
            "board_name", "created_at", "updated_at", "status_changes"
        }
        assert set(ticket_data.keys()) == required_fields

    def test_external_ticket_view_response_structure(self, client, sample_external_ticket):
        """Test external ticket view response has correct structure."""
        response = client.get(f"/api/public/tickets/{sample_external_ticket.uuid}")

        assert response.status_code == 200
        data = response.json()

        # Should have 'data' wrapper
        assert "data" in data

        # Data should have all required fields for external ticket
        ticket_data = data["data"]
        required_fields = {
            "uuid", "title", "board_name",
            "external_url", "platform_type", "created_at"
        }
        assert set(ticket_data.keys()) == required_fields
