"""
Board service for managing ticket boards.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.board import Board
from app.models.board_keyword import BoardKeyword
from app.models.manager import Manager
from app.models.ticket import Ticket
from app.core.security import encrypt_data, decrypt_data


class BoardService:
    """Service for board operations."""

    def _encrypt_external_config(self, platform_type: Optional[str], config: Optional[dict]) -> Optional[dict]:
        """
        Encrypt sensitive fields in external platform configuration.

        Args:
            platform_type: 'jira' or 'trello'
            config: Platform configuration dictionary

        Returns:
            Configuration with encrypted sensitive fields
        """
        if not config or not platform_type:
            return config

        encrypted_config = config.copy()

        if platform_type == 'jira':
            if 'api_token' in encrypted_config:
                encrypted_config['api_token_encrypted'] = encrypt_data(encrypted_config.pop('api_token'))
        elif platform_type == 'trello':
            if 'api_key' in encrypted_config:
                encrypted_config['api_key_encrypted'] = encrypt_data(encrypted_config.pop('api_key'))
            if 'api_token' in encrypted_config:
                encrypted_config['api_token_encrypted'] = encrypt_data(encrypted_config.pop('api_token'))

        return encrypted_config

    def _decrypt_external_config(self, platform_type: Optional[str], config: Optional[dict]) -> Optional[dict]:
        """
        Decrypt sensitive fields in external platform configuration.

        Args:
            platform_type: 'jira' or 'trello'
            config: Platform configuration dictionary with encrypted fields

        Returns:
            Configuration with decrypted sensitive fields
        """
        if not config or not platform_type:
            return config

        decrypted_config = config.copy()

        if platform_type == 'jira':
            if 'api_token_encrypted' in decrypted_config:
                decrypted_config['api_token'] = decrypt_data(decrypted_config.pop('api_token_encrypted'))
        elif platform_type == 'trello':
            if 'api_key_encrypted' in decrypted_config:
                decrypted_config['api_key'] = decrypt_data(decrypted_config.pop('api_key_encrypted'))
            if 'api_token_encrypted' in decrypted_config:
                decrypted_config['api_token'] = decrypt_data(decrypted_config.pop('api_token_encrypted'))

        return decrypted_config

    def _get_ticket_counts(self, db: Session, board_id: int) -> Dict[str, int]:
        """
        Get ticket counts by state for a board.

        Args:
            db: Database session
            board_id: Board ID

        Returns:
            Dictionary with counts by state
        """
        counts = db.query(
            Ticket.state,
            func.count(Ticket.id).label('count')
        ).filter(
            Ticket.board_id == board_id
        ).group_by(Ticket.state).all()

        result = {
            'new': 0,
            'in_progress': 0,
            'closed': 0,
            'rejected': 0
        }

        for state, count in counts:
            result[state] = count

        return result

    def create_board(
        self,
        db: Session,
        manager: Manager,
        name: str,
        unique_name: str,
        greeting_message: Optional[str] = None,
        exclusive_inbox_id: Optional[int] = None,
        external_platform_type: Optional[str] = None,
        external_platform_config: Optional[dict] = None
    ) -> Board:
        """
        Create a new board.

        Args:
            db: Database session
            manager: Manager instance
            name: Board display name
            unique_name: URL-safe slug
            greeting_message: Optional greeting message
            exclusive_inbox_id: Optional exclusive inbox
            external_platform_type: Optional 'jira' or 'trello'
            external_platform_config: Optional platform configuration

        Returns:
            Created Board instance

        Raises:
            HTTPException: If unique_name already exists or exclusive_inbox doesn't belong to manager
        """
        # Check if unique_name already exists
        existing = db.query(Board).filter(Board.unique_name == unique_name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Board with unique_name '{unique_name}' already exists"
            )

        # Validate exclusive_inbox belongs to manager if provided
        if exclusive_inbox_id:
            from app.models.email_inbox import EmailInbox
            inbox = db.query(EmailInbox).filter(
                EmailInbox.id == exclusive_inbox_id,
                EmailInbox.manager_id == manager.id
            ).first()
            if not inbox:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Inbox {exclusive_inbox_id} not found or doesn't belong to you"
                )

        # Encrypt external platform config if provided
        encrypted_config = self._encrypt_external_config(external_platform_type, external_platform_config)

        # Create board
        board = Board(
            manager_id=manager.id,
            name=name,
            unique_name=unique_name,
            greeting_message=greeting_message,
            exclusive_inbox_id=exclusive_inbox_id,
            external_platform_type=external_platform_type,
            external_platform_config=encrypted_config
        )

        db.add(board)
        db.commit()
        db.refresh(board)

        return board

    def get_boards(
        self,
        db: Session,
        manager: Manager,
        include_archived: bool = False
    ) -> List[tuple[Board, Dict[str, int]]]:
        """
        Get all boards for a manager with ticket counts.

        Args:
            db: Database session
            manager: Manager instance
            include_archived: Include archived boards

        Returns:
            List of tuples (Board, ticket_counts_dict)
        """
        query = db.query(Board).filter(Board.manager_id == manager.id)

        if not include_archived:
            query = query.filter(Board.is_archived == False)

        boards = query.order_by(Board.created_at.desc()).all()

        # Get ticket counts for each board
        result = []
        for board in boards:
            ticket_counts = self._get_ticket_counts(db, board.id)
            result.append((board, ticket_counts))

        return result

    def get_board(self, db: Session, manager: Manager, board_id: int) -> tuple[Board, Dict[str, int]]:
        """
        Get a specific board by ID with ticket counts.

        Args:
            db: Database session
            manager: Manager instance
            board_id: Board ID

        Returns:
            Tuple of (Board, ticket_counts_dict)

        Raises:
            HTTPException: If board not found or doesn't belong to manager
        """
        board = db.query(Board).filter(
            Board.id == board_id,
            Board.manager_id == manager.id
        ).first()

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Board {board_id} not found"
            )

        ticket_counts = self._get_ticket_counts(db, board.id)
        return board, ticket_counts

    def update_board(
        self,
        db: Session,
        manager: Manager,
        board_id: int,
        **update_data
    ) -> Board:
        """
        Update a board.

        Args:
            db: Database session
            manager: Manager instance
            board_id: Board ID
            **update_data: Fields to update

        Returns:
            Updated Board instance

        Raises:
            HTTPException: If board not found, unique_name conflict, or invalid exclusive_inbox
        """
        board = db.query(Board).filter(
            Board.id == board_id,
            Board.manager_id == manager.id
        ).first()

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Board {board_id} not found"
            )

        # Check unique_name uniqueness if being updated
        if 'unique_name' in update_data and update_data['unique_name'] != board.unique_name:
            existing = db.query(Board).filter(
                Board.unique_name == update_data['unique_name']
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Board with unique_name '{update_data['unique_name']}' already exists"
                )

        # Validate exclusive_inbox if being updated
        if 'exclusive_inbox_id' in update_data and update_data['exclusive_inbox_id']:
            from app.models.email_inbox import EmailInbox
            inbox = db.query(EmailInbox).filter(
                EmailInbox.id == update_data['exclusive_inbox_id'],
                EmailInbox.manager_id == manager.id
            ).first()
            if not inbox:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Inbox {update_data['exclusive_inbox_id']} not found or doesn't belong to you"
                )

        # Handle external platform config encryption
        if 'external_platform_config' in update_data:
            platform_type = update_data.get('external_platform_type', board.external_platform_type)
            update_data['external_platform_config'] = self._encrypt_external_config(
                platform_type,
                update_data['external_platform_config']
            )

        # Update fields
        for key, value in update_data.items():
            setattr(board, key, value)

        db.commit()
        db.refresh(board)

        return board

    def delete_board(self, db: Session, manager: Manager, board_id: int) -> None:
        """
        Delete a board (only if all tickets are rejected or no tickets exist).

        Args:
            db: Database session
            manager: Manager instance
            board_id: Board ID

        Raises:
            HTTPException: If board not found or has active tickets
        """
        board = db.query(Board).filter(
            Board.id == board_id,
            Board.manager_id == manager.id
        ).first()

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Board {board_id} not found"
            )

        # Check if board has non-rejected tickets
        active_tickets = db.query(Ticket).filter(
            Ticket.board_id == board_id,
            Ticket.state != 'rejected'
        ).count()

        if active_tickets > 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot delete board with active tickets. Archive the board instead."
            )

        db.delete(board)
        db.commit()

    def archive_board(self, db: Session, manager: Manager, board_id: int) -> Board:
        """
        Archive a board.

        Args:
            db: Database session
            manager: Manager instance
            board_id: Board ID

        Returns:
            Updated Board instance

        Raises:
            HTTPException: If board not found
        """
        board = db.query(Board).filter(
            Board.id == board_id,
            Board.manager_id == manager.id
        ).first()

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Board {board_id} not found"
            )

        board.is_archived = True
        db.commit()
        db.refresh(board)

        return board

    def test_external_connection(
        self,
        db: Session,
        manager: Manager,
        board_id: int
    ) -> Dict[str, str]:
        """
        Test external platform connection for a board.

        Args:
            db: Database session
            manager: Manager instance
            board_id: Board ID

        Returns:
            Dictionary with 'status' and 'message'

        Raises:
            HTTPException: If board not found or no external platform configured
        """
        board = db.query(Board).filter(
            Board.id == board_id,
            Board.manager_id == manager.id
        ).first()

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Board {board_id} not found"
            )

        if not board.external_platform_type or not board.external_platform_config:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No external platform configured for this board"
            )

        # Decrypt config for testing
        config = self._decrypt_external_config(
            board.external_platform_type,
            board.external_platform_config
        )

        # TODO: Implement actual connection testing for Jira and Trello
        # For now, return a placeholder response
        platform_name = board.external_platform_type.capitalize()

        # Placeholder - actual implementation would test the connection
        return {
            'status': 'success',
            'message': f'Successfully connected to {platform_name}'
        }

    # Board Keyword methods
    def get_keywords(self, db: Session, manager: Manager, board_id: int) -> List[BoardKeyword]:
        """
        Get all keywords for a board.

        Args:
            db: Database session
            manager: Manager instance
            board_id: Board ID

        Returns:
            List of BoardKeyword instances

        Raises:
            HTTPException: If board not found or doesn't belong to manager
        """
        # Verify board belongs to manager
        board = db.query(Board).filter(
            Board.id == board_id,
            Board.manager_id == manager.id
        ).first()

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Board {board_id} not found"
            )

        return db.query(BoardKeyword).filter(
            BoardKeyword.board_id == board_id
        ).order_by(BoardKeyword.created_at.desc()).all()

    def create_keyword(
        self,
        db: Session,
        manager: Manager,
        board_id: int,
        keyword: str
    ) -> BoardKeyword:
        """
        Create a new keyword for a board.

        Validates that the keyword is unique across all manager's boards.

        Args:
            db: Database session
            manager: Manager instance
            board_id: Board ID
            keyword: Keyword string

        Returns:
            Created BoardKeyword instance

        Raises:
            HTTPException: If board not found, keyword conflicts, or board doesn't belong to manager
        """
        # Verify board belongs to manager
        board = db.query(Board).filter(
            Board.id == board_id,
            Board.manager_id == manager.id
        ).first()

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Board {board_id} not found"
            )

        # Check if keyword already exists on any of manager's boards
        # Case-insensitive check
        existing_keyword = db.query(BoardKeyword).join(Board).filter(
            Board.manager_id == manager.id,
            func.lower(BoardKeyword.keyword) == func.lower(keyword)
        ).first()

        if existing_keyword:
            # Get the board name for the error message
            conflicting_board = db.query(Board).filter(
                Board.id == existing_keyword.board_id
            ).first()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Keyword '{keyword}' is already assigned to board '{conflicting_board.name}'"
            )

        # Create keyword
        board_keyword = BoardKeyword(
            board_id=board_id,
            keyword=keyword
        )

        db.add(board_keyword)
        db.commit()
        db.refresh(board_keyword)

        return board_keyword

    def delete_keyword(
        self,
        db: Session,
        manager: Manager,
        board_id: int,
        keyword_id: int
    ) -> None:
        """
        Delete a keyword from a board.

        Args:
            db: Database session
            manager: Manager instance
            board_id: Board ID
            keyword_id: Keyword ID

        Raises:
            HTTPException: If board or keyword not found, or doesn't belong to manager
        """
        # Verify board belongs to manager
        board = db.query(Board).filter(
            Board.id == board_id,
            Board.manager_id == manager.id
        ).first()

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Board {board_id} not found"
            )

        # Find and delete keyword
        keyword = db.query(BoardKeyword).filter(
            BoardKeyword.id == keyword_id,
            BoardKeyword.board_id == board_id
        ).first()

        if not keyword:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Keyword {keyword_id} not found on board {board_id}"
            )

        db.delete(keyword)
        db.commit()


# Singleton instance
board_service = BoardService()
