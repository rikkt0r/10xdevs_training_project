"""add all remaining models

Revision ID: b7375bf8a9b5
Revises: 1becd249597c
Create Date: 2026-01-18 23:29:35.399661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b7375bf8a9b5'
down_revision: Union[str, None] = '1becd249597c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create email_inboxes table
    op.create_table(
        'email_inboxes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manager_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('imap_host', sa.String(length=255), nullable=False),
        sa.Column('imap_port', sa.Integer(), nullable=False, server_default='993'),
        sa.Column('imap_username', sa.String(length=255), nullable=False),
        sa.Column('imap_password_encrypted', sa.Text(), nullable=False),
        sa.Column('imap_use_ssl', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('smtp_host', sa.String(length=255), nullable=False),
        sa.Column('smtp_port', sa.Integer(), nullable=False, server_default='587'),
        sa.Column('smtp_username', sa.String(length=255), nullable=False),
        sa.Column('smtp_password_encrypted', sa.Text(), nullable=False),
        sa.Column('smtp_use_tls', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('from_address', sa.String(length=255), nullable=False),
        sa.Column('polling_interval', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('last_polled_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('polling_interval IN (1, 5, 15)', name='check_polling_interval'),
        sa.ForeignKeyConstraint(['manager_id'], ['managers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_email_inboxes_manager', 'email_inboxes', ['manager_id'])
    op.create_index('idx_email_inboxes_active_polling', 'email_inboxes', ['is_active', 'last_polled_at'], postgresql_where=sa.text('is_active = true'))

    # Create boards table
    op.create_table(
        'boards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manager_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('unique_name', sa.String(length=255), nullable=False),
        sa.Column('greeting_message', sa.Text(), nullable=True),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('external_platform_type', sa.String(length=20), nullable=True),
        sa.Column('external_platform_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('exclusive_inbox_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint("external_platform_type IS NULL OR external_platform_type IN ('jira', 'trello')", name='check_external_platform_type'),
        sa.CheckConstraint("unique_name ~ '^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'", name='check_unique_name_format'),
        sa.ForeignKeyConstraint(['exclusive_inbox_id'], ['email_inboxes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['manager_id'], ['managers.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('unique_name')
    )
    op.create_index('idx_boards_manager', 'boards', ['manager_id'])
    op.create_index('idx_boards_unique_name', 'boards', ['unique_name'])
    op.create_index('idx_boards_exclusive_inbox', 'boards', ['exclusive_inbox_id'], postgresql_where=sa.text('exclusive_inbox_id IS NOT NULL'))

    # Create board_keywords table
    op.create_table(
        'board_keywords',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('board_id', sa.Integer(), nullable=False),
        sa.Column('keyword', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['board_id'], ['boards.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('board_id', 'keyword', name='uq_board_keyword')
    )
    op.create_index('idx_board_keywords_board', 'board_keywords', ['board_id'])
    op.create_index('idx_board_keywords_keyword_lower', 'board_keywords', [sa.text('LOWER(keyword)')])

    # Create tickets table
    op.create_table(
        'tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('board_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('state', sa.String(length=20), nullable=False, server_default='new'),
        sa.Column('creator_email', sa.String(length=255), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False, server_default='web'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint("state IN ('new', 'in_progress', 'closed', 'rejected')", name='check_ticket_state'),
        sa.CheckConstraint("source IN ('web', 'email')", name='check_ticket_source'),
        sa.ForeignKeyConstraint(['board_id'], ['boards.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.create_index('idx_tickets_uuid', 'tickets', ['uuid'])
    op.create_index('idx_tickets_board', 'tickets', ['board_id'])
    op.create_index('idx_tickets_board_state', 'tickets', ['board_id', 'state'])
    op.create_index('idx_tickets_board_created', 'tickets', ['board_id', 'created_at'])
    op.create_index('idx_tickets_creator_email', 'tickets', ['creator_email'])

    # Create ticket_status_changes table
    op.create_table(
        'ticket_status_changes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('previous_state', sa.String(length=20), nullable=False),
        sa.Column('new_state', sa.String(length=20), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint("previous_state IN ('new', 'in_progress', 'closed', 'rejected')", name='check_previous_state'),
        sa.CheckConstraint("new_state IN ('new', 'in_progress', 'closed', 'rejected')", name='check_new_state'),
        sa.CheckConstraint('previous_state <> new_state', name='check_state_different'),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ticket_status_changes_ticket', 'ticket_status_changes', ['ticket_id'])
    op.create_index('idx_ticket_status_changes_ticket_created', 'ticket_status_changes', ['ticket_id', 'created_at'])

    # Create external_tickets table
    op.create_table(
        'external_tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('board_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('creator_email', sa.String(length=255), nullable=False),
        sa.Column('external_url', sa.String(length=2048), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('platform_type', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint("platform_type IN ('jira', 'trello')", name='check_platform_type'),
        sa.ForeignKeyConstraint(['board_id'], ['boards.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.create_index('idx_external_tickets_uuid', 'external_tickets', ['uuid'])
    op.create_index('idx_external_tickets_board', 'external_tickets', ['board_id'])
    op.create_index('idx_external_tickets_creator_email', 'external_tickets', ['creator_email'])

    # Create standby_queue_items table
    op.create_table(
        'standby_queue_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manager_id', sa.Integer(), nullable=False),
        sa.Column('email_subject', sa.String(length=255), nullable=False),
        sa.Column('email_body', sa.Text(), nullable=False),
        sa.Column('sender_email', sa.String(length=255), nullable=False),
        sa.Column('failure_reason', sa.String(length=50), nullable=False),
        sa.Column('original_board_id', sa.Integer(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint("failure_reason IN ('no_keyword_match', 'external_creation_failed', 'no_board_match')", name='check_failure_reason'),
        sa.ForeignKeyConstraint(['manager_id'], ['managers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['original_board_id'], ['boards.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_standby_queue_manager', 'standby_queue_items', ['manager_id'])
    op.create_index('idx_standby_queue_manager_created', 'standby_queue_items', ['manager_id', 'created_at'])

    # Create processed_emails table
    op.create_table(
        'processed_emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inbox_id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.String(length=255), nullable=False),
        sa.Column('sender_email', sa.String(length=255), nullable=False),
        sa.Column('subject_hash', sa.String(length=64), nullable=False),
        sa.Column('processed_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['inbox_id'], ['email_inboxes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inbox_id', 'message_id', name='uq_inbox_message')
    )
    op.create_index('idx_processed_emails_inbox_message', 'processed_emails', ['inbox_id', 'message_id'])
    op.create_index('idx_processed_emails_duplicate_check', 'processed_emails', ['inbox_id', 'sender_email', 'subject_hash', 'processed_at'])


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table('processed_emails')
    op.drop_table('standby_queue_items')
    op.drop_table('external_tickets')
    op.drop_table('ticket_status_changes')
    op.drop_table('tickets')
    op.drop_table('board_keywords')
    op.drop_table('boards')
    op.drop_table('email_inboxes')
