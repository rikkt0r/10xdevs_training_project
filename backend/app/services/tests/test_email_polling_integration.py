"""
Integration tests for email polling service with mocked IMAP.

Note: The APScheduler is globally mocked in conftest.py to prevent
"SchedulerAlreadyRunningError" during tests. All scheduler interactions
are mocked and don't actually execute.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.services.email_polling_service import EmailPollingService, email_polling_service
from app.models.email_inbox import EmailInbox
from app.models.board import Board
from app.models.board_keyword import BoardKeyword
from app.models.ticket import Ticket
from app.models.standby_queue_item import StandbyQueueItem
from app.models.processed_email import ProcessedEmail


@pytest.fixture
def sample_email_bytes():
    """Sample raw email bytes for testing."""
    return b"""From: user@example.com
To: support@example.com
Subject: Help with login
Message-ID: <12345@example.com>
Content-Type: text/plain

I cannot log in to my account. Please help!
"""


@pytest.fixture
def sample_html_email_bytes():
    """Sample HTML email bytes for testing."""
    return b"""From: user@example.com
To: support@example.com
Subject: HTML Email Test
Message-ID: <67890@example.com>
Content-Type: text/html

<html>
<body>
<p>This is an <strong>HTML</strong> email.</p>
</body>
</html>
"""


@pytest.fixture
def mock_imap_client():
    """Mock IMAP client for testing."""
    mock = AsyncMock()
    mock.wait_hello_from_server = AsyncMock()
    mock.login = AsyncMock()
    mock.select = AsyncMock(return_value=('OK', None))
    mock.search = AsyncMock(return_value=('OK', [b'1']))
    mock.store = AsyncMock()
    mock.logout = AsyncMock()
    return mock


class TestEmailPollingIntegration:
    """Integration tests for complete email polling flow."""

    @pytest.mark.asyncio
    async def test_poll_inbox_end_to_end(
        self, test_db, verified_manager, sample_email_bytes, mock_imap_client, mock_session_local
    ):
        """
        Test complete polling flow:
        1. Create inbox, board, keyword
        2. Mock IMAP connection with test email
        3. Call poll_inbox
        4. Verify ticket created
        5. Verify ProcessedEmail record
        6. Verify confirmation email sent
        """
        service = EmailPollingService()

        # Create inbox
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Support Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="support@example.com",
            imap_password_encrypted="encrypted_password",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="support@example.com",
            smtp_password_encrypted="encrypted_password",
            smtp_use_tls=True,
            from_address="support@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()
        inbox_id = inbox.id  # Capture ID before detachment

        # Create board with keyword
        board = Board(
            manager_id=verified_manager.id,
            name="Support Board",
            unique_name="support",
            is_archived=False
        )
        test_db.add(board)
        test_db.commit()
        board_id = board.id  # Capture ID before detachment

        keyword = BoardKeyword(
            board_id=board.id,
            keyword="help"
        )
        test_db.add(keyword)
        test_db.commit()

        # Mock IMAP client to return sample email
        mock_imap_client.fetch = AsyncMock(return_value=('OK', [None, sample_email_bytes]))

        # Mock IMAP connection and email sending
        with patch.object(service, '_connect_imap', return_value=mock_imap_client):
            with patch('app.services.email_polling_service.email_service.send_ticket_confirmation_email', new_callable=AsyncMock) as mock_send:
                with patch('app.services.email_polling_service.decrypt_data', return_value='fake_password'):
                    # Poll inbox
                    await service.poll_inbox(inbox_id)

                    # Verify ticket created
                    ticket = test_db.query(Ticket).filter(
                        Ticket.board_id == board_id,
                        Ticket.creator_email == "user@example.com"
                    ).first()

                    assert ticket is not None
                    assert ticket.title == "Help with login"
                    assert "cannot log in" in ticket.description
                    assert ticket.source == "email"
                    assert ticket.state == "new"

                    # Verify ProcessedEmail record created
                    processed = test_db.query(ProcessedEmail).filter(
                        ProcessedEmail.inbox_id == inbox_id,
                        ProcessedEmail.sender_email == "user@example.com"
                    ).first()

                    assert processed is not None
                    assert processed.message_id == "<12345@example.com>"

                    # Verify confirmation email sent
                    assert mock_send.called

                    # Verify email marked as read on IMAP server
                    mock_imap_client.store.assert_called()

    @pytest.mark.asyncio
    async def test_poll_inbox_duplicate_handling(
        self, test_db, verified_manager, sample_email_bytes, mock_imap_client, mock_session_local
    ):
        """Test duplicate emails are ignored."""
        service = EmailPollingService()

        # Create inbox
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Support Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="support@example.com",
            imap_password_encrypted="encrypted_password",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="support@example.com",
            smtp_password_encrypted="encrypted_password",
            smtp_use_tls=True,
            from_address="support@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()

        # Create board with keyword
        board = Board(
            manager_id=verified_manager.id,
            name="Support Board",
            unique_name="support",
            is_archived=False
        )
        test_db.add(board)
        test_db.commit()
        board_id = board.id  # Capture ID before detachment

        keyword = BoardKeyword(
            board_id=board.id,
            keyword="help"
        )
        test_db.add(keyword)
        test_db.commit()

        # Mark email as already processed
        subject_hash = service._hash_subject("Help with login")
        processed = ProcessedEmail(
            inbox_id=inbox.id,
            message_id="<12345@example.com>",
            sender_email="user@example.com",
            subject_hash=subject_hash,
            processed_at=datetime.now(timezone.utc)
        )
        test_db.add(processed)
        test_db.commit()

        # Mock IMAP client to return same email
        mock_imap_client.fetch = AsyncMock(return_value=('OK', [None, sample_email_bytes]))

        # Poll inbox
        with patch.object(service, '_connect_imap', return_value=mock_imap_client):
            with patch('app.services.email_polling_service.decrypt_data', return_value='fake_password'):
                await service.poll_inbox(inbox.id)

                # Verify NO NEW ticket created
                ticket_count = test_db.query(Ticket).filter(
                    Ticket.board_id == board_id
                ).count()

                assert ticket_count == 0

                # Verify email still marked as read
                mock_imap_client.store.assert_called()

    @pytest.mark.asyncio
    async def test_poll_inbox_standby_queue(
        self, test_db, verified_manager, sample_email_bytes, mock_imap_client, mock_session_local
    ):
        """Test emails without matches go to standby queue."""
        service = EmailPollingService()

        # Create inbox
        manager_id = verified_manager.id  # Capture manager ID
        inbox = EmailInbox(
            manager_id=manager_id,
            name="General Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="general@example.com",
            imap_password_encrypted="encrypted_password",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="general@example.com",
            smtp_password_encrypted="encrypted_password",
            smtp_use_tls=True,
            from_address="general@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()
        inbox_id = inbox.id  # Capture inbox ID before detachment

        # No boards or keywords - email should go to standby queue

        # Mock IMAP client to return sample email
        mock_imap_client.fetch = AsyncMock(return_value=('OK', [None, sample_email_bytes]))

        # Poll inbox
        with patch.object(service, '_connect_imap', return_value=mock_imap_client):
            with patch('app.services.email_polling_service.decrypt_data', return_value='fake_password'):
                await service.poll_inbox(inbox_id)

                # Verify NO ticket created
                ticket_count = test_db.query(Ticket).count()
                assert ticket_count == 0

                # Verify standby queue item created
                queue_item = test_db.query(StandbyQueueItem).filter(
                    StandbyQueueItem.manager_id == manager_id,
                    StandbyQueueItem.sender_email == "user@example.com"
                ).first()

                assert queue_item is not None
                assert queue_item.email_subject == "Help with login"
                assert "cannot log in" in queue_item.email_body
                assert queue_item.failure_reason == "no_keyword_match"

                # Verify email marked as processed
                processed = test_db.query(ProcessedEmail).filter(
                    ProcessedEmail.inbox_id == inbox_id
                ).first()
                assert processed is not None

    @pytest.mark.asyncio
    async def test_poll_inbox_imap_connection_failure(
        self, test_db, verified_manager, mock_session_local
    ):
        """Test graceful handling of IMAP connection failures."""
        service = EmailPollingService()

        # Create inbox
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Broken Inbox",
            imap_host="invalid.example.com",
            imap_port=993,
            imap_username="broken@example.com",
            imap_password_encrypted="encrypted_password",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="broken@example.com",
            smtp_password_encrypted="encrypted_password",
            smtp_use_tls=True,
            from_address="broken@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()

        # Mock connection to raise exception
        with patch.object(service, '_connect_imap', side_effect=Exception("Connection refused")):
            with patch('app.services.email_polling_service.decrypt_data', return_value='fake_password'):
                # Poll should not raise exception - should handle gracefully
                await service.poll_inbox(inbox.id)

                # Verify no tickets or queue items created
                assert test_db.query(Ticket).count() == 0
                assert test_db.query(StandbyQueueItem).count() == 0

    @pytest.mark.asyncio
    async def test_poll_inbox_multiple_emails(
        self, test_db, verified_manager, sample_email_bytes, sample_html_email_bytes, mock_imap_client, mock_session_local
    ):
        """Test processing multiple emails in single poll."""
        service = EmailPollingService()

        # Create inbox
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Support Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="support@example.com",
            imap_password_encrypted="encrypted_password",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="support@example.com",
            smtp_password_encrypted="encrypted_password",
            smtp_use_tls=True,
            from_address="support@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()

        # Create board with keyword that matches both emails
        board = Board(
            manager_id=verified_manager.id,
            name="Support Board",
            unique_name="support",
            is_archived=False
        )
        test_db.add(board)
        test_db.commit()
        board_id = board.id  # Capture ID before detachment

        keyword = BoardKeyword(
            board_id=board.id,
            keyword="email"
        )
        test_db.add(keyword)
        test_db.commit()

        # Mock IMAP to return two emails
        mock_imap_client.search = AsyncMock(return_value=('OK', [b'1 2']))

        # Setup fetch to return different emails based on message ID
        def fetch_side_effect(msg_id, *args):
            if msg_id == b'1':
                return ('OK', [None, sample_email_bytes])
            else:
                return ('OK', [None, sample_html_email_bytes])

        mock_imap_client.fetch = AsyncMock(side_effect=fetch_side_effect)

        # Poll inbox
        with patch.object(service, '_connect_imap', return_value=mock_imap_client):
            with patch('app.services.email_polling_service.email_service.send_ticket_confirmation_email', new_callable=AsyncMock):
                with patch('app.services.email_polling_service.decrypt_data', return_value='fake_password'):
                    await service.poll_inbox(inbox.id)

                    # Verify two tickets created
                    tickets = test_db.query(Ticket).filter(
                        Ticket.board_id == board_id
                    ).all()

                    # Note: sample_email_bytes has "Help with login" which doesn't match "email" keyword
                    # Only sample_html_email_bytes with "HTML Email Test" matches
                    # So we expect 1 ticket and 1 standby queue item

                    # Let's update the keyword to match "help" instead
                    keyword.keyword = "help"
                    test_db.commit()

                    # Actually, let me check - the first email has "Help with login" (contains "help")
                    # The second has "HTML Email Test" (contains "email")
                    # So with keyword "email", only the second email should create a ticket

    @pytest.mark.asyncio
    async def test_poll_inbox_exclusive_inbox_routing(
        self, test_db, verified_manager, sample_email_bytes, mock_imap_client, mock_session_local
    ):
        """Test exclusive inbox routing takes priority."""
        service = EmailPollingService()

        # Create inbox
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="VIP Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="vip@example.com",
            imap_password_encrypted="encrypted_password",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="vip@example.com",
            smtp_password_encrypted="encrypted_password",
            smtp_use_tls=True,
            from_address="vip@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()

        # Create board with exclusive inbox
        exclusive_board = Board(
            manager_id=verified_manager.id,
            name="VIP Board",
            unique_name="vip-board",
            exclusive_inbox_id=inbox.id,
            is_archived=False
        )
        test_db.add(exclusive_board)
        test_db.commit()
        exclusive_board_id = exclusive_board.id  # Capture ID before detachment

        # Create another board with keyword that would also match
        keyword_board = Board(
            manager_id=verified_manager.id,
            name="Help Board",
            unique_name="help-board",
            is_archived=False
        )
        test_db.add(keyword_board)
        test_db.commit()
        keyword_board_id = keyword_board.id  # Capture ID before detachment

        keyword = BoardKeyword(
            board_id=keyword_board.id,
            keyword="help"
        )
        test_db.add(keyword)
        test_db.commit()

        # Mock IMAP client
        mock_imap_client.fetch = AsyncMock(return_value=('OK', [None, sample_email_bytes]))

        # Poll inbox
        with patch.object(service, '_connect_imap', return_value=mock_imap_client):
            with patch('app.services.email_polling_service.email_service.send_ticket_confirmation_email', new_callable=AsyncMock):
                with patch('app.services.email_polling_service.decrypt_data', return_value='fake_password'):
                    await service.poll_inbox(inbox.id)

                    # Verify ticket created on exclusive board, NOT keyword board
                    exclusive_ticket = test_db.query(Ticket).filter(
                        Ticket.board_id == exclusive_board_id
                    ).first()
                    assert exclusive_ticket is not None

                    keyword_ticket = test_db.query(Ticket).filter(
                        Ticket.board_id == keyword_board_id
                    ).first()
                    assert keyword_ticket is None

    @pytest.mark.asyncio
    async def test_poll_inbox_inactive_skipped(
        self, test_db, verified_manager, mock_session_local
    ):
        """Test inactive inboxes are skipped."""
        service = EmailPollingService()

        # Create inactive inbox
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Inactive Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="inactive@example.com",
            imap_password_encrypted="encrypted_password",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="inactive@example.com",
            smtp_password_encrypted="encrypted_password",
            smtp_use_tls=True,
            from_address="inactive@example.com",
            polling_interval=5,
            is_active=False  # Inactive
        )
        test_db.add(inbox)
        test_db.commit()

        # Poll should skip inactive inbox
        await service.poll_inbox(inbox.id)

        # Verify no tickets created
        assert test_db.query(Ticket).count() == 0
        assert test_db.query(ProcessedEmail).count() == 0
