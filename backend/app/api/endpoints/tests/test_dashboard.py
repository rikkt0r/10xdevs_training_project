"""
Tests for dashboard statistics endpoints.
"""
import pytest
from datetime import datetime, timezone, timedelta

from app.models.board import Board
from app.models.ticket import Ticket
from app.models.standby_queue_item import StandbyQueueItem


# Fixtures

@pytest.fixture
def setup_dashboard_data(test_db, verified_manager, other_manager):
    """
    Create comprehensive test data for dashboard statistics.

    Creates for verified_manager:
    - 5 boards total (4 active, 1 archived)
    - 3 standby queue items
    - Tickets in various states
    - Tickets created today and this week
    """
    # Create boards for verified_manager
    boards = []
    for i in range(5):
        board = Board(
            manager_id=verified_manager.id,
            name=f"Board {i+1}",
            unique_name=f"board-{i+1}",
            greeting_message=f"Welcome to board {i+1}",
            is_archived=(i == 4)  # Last board is archived
        )
        boards.append(board)
        test_db.add(board)

    # Create board for other_manager (should not be counted)
    other_board = Board(
        manager_id=other_manager.id,
        name="Other Manager Board",
        unique_name="other-board",
        is_archived=False
    )
    test_db.add(other_board)

    test_db.commit()
    for board in boards:
        test_db.refresh(board)
    test_db.refresh(other_board)

    # Create standby queue items for verified_manager
    for i in range(3):
        item = StandbyQueueItem(
            manager_id=verified_manager.id,
            email_subject=f"Queue item {i+1}",
            email_body="Test body",
            sender_email=f"user{i+1}@example.com",
            failure_reason="no_keyword_match",
            retry_count=0
        )
        test_db.add(item)

    # Create standby queue item for other_manager (should not be counted)
    other_item = StandbyQueueItem(
        manager_id=other_manager.id,
        email_subject="Other queue item",
        email_body="Test body",
        sender_email="other@example.com",
        failure_reason="no_keyword_match",
        retry_count=0
    )
    test_db.add(other_item)

    test_db.commit()

    # Create tickets in various states
    # Use a fixed reference time (Wednesday at 18:00 UTC) to avoid test flakiness
    now = datetime.now(timezone.utc)
    # Calculate today at 00:00 and yesterday
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    # Tickets created today (use current time minus a few hours)
    today_tickets = [
        {"state": "new", "hours_ago": 2},
        {"state": "new", "hours_ago": 4},
        {"state": "in_progress", "hours_ago": 6},
        {"state": "closed", "hours_ago": 8},
        {"state": "rejected", "hours_ago": 10}
    ]

    for ticket_data in today_tickets:
        ticket = Ticket(
            board_id=boards[0].id,
            title=f"Ticket {ticket_data['state']}",
            description="Test description",
            creator_email="user@example.com",
            source="web",
            state=ticket_data['state']
        )
        test_db.add(ticket)
        test_db.flush()
        # Set to today but earlier
        ticket.created_at = now - timedelta(hours=ticket_data['hours_ago'])

    # Tickets created yesterday (guaranteed to be this week if today is Tue-Sun)
    # If today is Monday, these will be in previous week, so we'll adjust expectations
    yesterday = today_start - timedelta(days=1)
    week_tickets = [
        {"state": "new", "time": datetime(yesterday.year, yesterday.month, yesterday.day, 10, 0, tzinfo=timezone.utc)},
        {"state": "in_progress", "time": datetime(yesterday.year, yesterday.month, yesterday.day, 14, 0, tzinfo=timezone.utc)},
        {"state": "closed", "time": datetime(yesterday.year, yesterday.month, yesterday.day, 18, 0, tzinfo=timezone.utc)}
    ]

    for ticket_data in week_tickets:
        ticket = Ticket(
            board_id=boards[1].id,
            title=f"Week ticket {ticket_data['state']}",
            description="Test description",
            creator_email="user@example.com",
            source="email",
            state=ticket_data['state']
        )
        test_db.add(ticket)
        test_db.flush()
        ticket.created_at = ticket_data['time']

    # Tickets created last week (should not be counted in this week)
    old_tickets = [
        {"state": "new", "days_ago": 10},
        {"state": "in_progress", "days_ago": 15},
        {"state": "closed", "days_ago": 20}
    ]

    for ticket_data in old_tickets:
        ticket = Ticket(
            board_id=boards[2].id,
            title=f"Old ticket {ticket_data['state']}",
            description="Test description",
            creator_email="user@example.com",
            source="web",
            state=ticket_data['state']
        )
        test_db.add(ticket)
        test_db.flush()
        ticket.created_at = now - timedelta(days=ticket_data['days_ago'])

    # Create tickets for other_manager (should not be counted)
    other_ticket = Ticket(
        board_id=other_board.id,
        title="Other manager ticket",
        description="Test description",
        creator_email="other@example.com",
        source="web",
        state="new"
    )
    test_db.add(other_ticket)

    test_db.commit()

    # Calculate if yesterday's tickets are in this week
    # If today is Monday (weekday 0), yesterday was Sunday (previous week)
    is_monday = now.weekday() == 0
    yesterday_count_per_state = 0 if is_monday else 1  # 1 ticket per state yesterday

    return {
        "boards": boards,
        "expected_boards_count": 5,
        "expected_active_boards_count": 4,
        "expected_standby_queue_count": 3,
        "expected_tickets_by_state": {
            # Total = today + yesterday (if not Monday) + old
            "new": 2 + yesterday_count_per_state + 1,  # 2 today + maybe 1 yesterday + 1 old
            "in_progress": 1 + yesterday_count_per_state + 1,  # 1 today + maybe 1 yesterday + 1 old
            "closed": 1 + yesterday_count_per_state + 1,  # 1 today + maybe 1 yesterday + 1 old
            "rejected": 1  # 1 today only
        },
        "expected_tickets_today": 5,
        "expected_tickets_this_week": 5 + (3 if not is_monday else 0)  # 5 today + maybe 3 yesterday
    }


# Tests for GET /api/dashboard/stats

class TestGetDashboardStats:
    """Tests for getting dashboard statistics."""

    def test_get_stats_success(self, client, auth_headers, setup_dashboard_data):
        """Test successful retrieval of dashboard statistics."""
        expected = setup_dashboard_data

        response = client.get("/api/dashboard/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data

        stats = data["data"]
        assert stats["boards_count"] == expected["expected_boards_count"]
        assert stats["active_boards_count"] == expected["expected_active_boards_count"]
        assert stats["standby_queue_count"] == expected["expected_standby_queue_count"]

        # Check tickets by state
        assert "tickets_by_state" in stats
        assert stats["tickets_by_state"]["new"] == expected["expected_tickets_by_state"]["new"]
        assert stats["tickets_by_state"]["in_progress"] == expected["expected_tickets_by_state"]["in_progress"]
        assert stats["tickets_by_state"]["closed"] == expected["expected_tickets_by_state"]["closed"]
        assert stats["tickets_by_state"]["rejected"] == expected["expected_tickets_by_state"]["rejected"]

        # Check recent activity
        assert "recent_activity" in stats
        assert stats["recent_activity"]["tickets_created_today"] == expected["expected_tickets_today"]
        assert stats["recent_activity"]["tickets_created_this_week"] == expected["expected_tickets_this_week"]

    def test_get_stats_no_data(self, client, auth_headers):
        """Test dashboard stats when manager has no data."""
        response = client.get("/api/dashboard/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        stats = data["data"]

        # All counts should be zero
        assert stats["boards_count"] == 0
        assert stats["active_boards_count"] == 0
        assert stats["standby_queue_count"] == 0
        assert stats["tickets_by_state"]["new"] == 0
        assert stats["tickets_by_state"]["in_progress"] == 0
        assert stats["tickets_by_state"]["closed"] == 0
        assert stats["tickets_by_state"]["rejected"] == 0
        assert stats["recent_activity"]["tickets_created_today"] == 0
        assert stats["recent_activity"]["tickets_created_this_week"] == 0

    def test_get_stats_unauthenticated(self, client):
        """Test dashboard stats without authentication."""
        response = client.get("/api/dashboard/stats")

        assert response.status_code == 403

    def test_get_stats_invalid_token(self, client):
        """Test dashboard stats with invalid token."""
        response = client.get(
            "/api/dashboard/stats",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401

    def test_get_stats_only_active_boards(self, test_db, verified_manager, client, auth_headers):
        """Test that active_boards_count only includes non-archived boards."""
        # Create 2 active boards
        for i in range(2):
            board = Board(
                manager_id=verified_manager.id,
                name=f"Active Board {i+1}",
                unique_name=f"active-{i+1}",
                is_archived=False
            )
            test_db.add(board)

        # Create 3 archived boards
        for i in range(3):
            board = Board(
                manager_id=verified_manager.id,
                name=f"Archived Board {i+1}",
                unique_name=f"archived-{i+1}",
                is_archived=True
            )
            test_db.add(board)

        test_db.commit()

        response = client.get("/api/dashboard/stats", headers=auth_headers)

        assert response.status_code == 200
        stats = response.json()["data"]
        assert stats["boards_count"] == 5
        assert stats["active_boards_count"] == 2

    def test_get_stats_only_own_data(self, test_db, verified_manager, other_manager, client, auth_headers):
        """Test that manager only sees their own statistics."""
        # Create data for verified_manager
        board1 = Board(
            manager_id=verified_manager.id,
            name="My Board",
            unique_name="my-board",
            is_archived=False
        )
        test_db.add(board1)
        test_db.flush()

        ticket1 = Ticket(
            board_id=board1.id,
            title="My Ticket",
            description="Test",
            creator_email="user@example.com",
            source="web",
            state="new"
        )
        test_db.add(ticket1)

        # Create data for other_manager (should not be counted)
        board2 = Board(
            manager_id=other_manager.id,
            name="Other Board",
            unique_name="other-board",
            is_archived=False
        )
        test_db.add(board2)
        test_db.flush()

        ticket2 = Ticket(
            board_id=board2.id,
            title="Other Ticket",
            description="Test",
            creator_email="other@example.com",
            source="web",
            state="new"
        )
        test_db.add(ticket2)

        test_db.commit()

        response = client.get("/api/dashboard/stats", headers=auth_headers)

        assert response.status_code == 200
        stats = response.json()["data"]

        # Should only count verified_manager's data
        assert stats["boards_count"] == 1
        assert stats["active_boards_count"] == 1
        assert stats["tickets_by_state"]["new"] == 1
        assert stats["tickets_by_state"]["in_progress"] == 0
        assert stats["tickets_by_state"]["closed"] == 0
        assert stats["tickets_by_state"]["rejected"] == 0

    def test_get_stats_all_ticket_states(self, test_db, verified_manager, client, auth_headers):
        """Test ticket counts for all possible states."""
        board = Board(
            manager_id=verified_manager.id,
            name="Test Board",
            unique_name="test-board",
            is_archived=False
        )
        test_db.add(board)
        test_db.flush()

        # Create tickets in each state
        states = ["new", "new", "in_progress", "in_progress", "in_progress", "closed", "rejected"]
        for state in states:
            ticket = Ticket(
                board_id=board.id,
                title=f"Ticket {state}",
                description="Test",
                creator_email="user@example.com",
                source="web",
                state=state
            )
            test_db.add(ticket)

        test_db.commit()

        response = client.get("/api/dashboard/stats", headers=auth_headers)

        assert response.status_code == 200
        stats = response.json()["data"]
        assert stats["tickets_by_state"]["new"] == 2
        assert stats["tickets_by_state"]["in_progress"] == 3
        assert stats["tickets_by_state"]["closed"] == 1
        assert stats["tickets_by_state"]["rejected"] == 1


# Tests for response structure validation

class TestDashboardResponseStructure:
    """Tests for validating dashboard response structure."""

    def test_response_structure(self, client, auth_headers):
        """Test that dashboard stats response has correct structure."""
        response = client.get("/api/dashboard/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should have 'data' wrapper
        assert "data" in data
        assert set(data.keys()) == {"data"}

        # Data should have all required fields
        stats = data["data"]
        required_fields = {
            "boards_count",
            "active_boards_count",
            "standby_queue_count",
            "tickets_by_state",
            "recent_activity"
        }
        assert set(stats.keys()) == required_fields

        # tickets_by_state should have all states
        assert set(stats["tickets_by_state"].keys()) == {"new", "in_progress", "closed", "rejected"}

        # recent_activity should have correct fields
        assert set(stats["recent_activity"].keys()) == {"tickets_created_today", "tickets_created_this_week"}

        # All values should be integers
        assert isinstance(stats["boards_count"], int)
        assert isinstance(stats["active_boards_count"], int)
        assert isinstance(stats["standby_queue_count"], int)
        assert isinstance(stats["tickets_by_state"]["new"], int)
        assert isinstance(stats["tickets_by_state"]["in_progress"], int)
        assert isinstance(stats["tickets_by_state"]["closed"], int)
        assert isinstance(stats["tickets_by_state"]["rejected"], int)
        assert isinstance(stats["recent_activity"]["tickets_created_today"], int)
        assert isinstance(stats["recent_activity"]["tickets_created_this_week"], int)
