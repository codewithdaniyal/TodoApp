"""add messages table for chat history

Revision ID: 004_add_messages_table
Revises: b4504f3d3d25
Create Date: 2026-02-05

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '004_add_messages_table'
down_revision = 'b4504f3d3d25'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create messages table for AI chat conversation history."""

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),  # Changed from sa.String() to sa.Integer()
        sa.Column('thread_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Create indexes for performance
    op.create_index('ix_messages_user_id', 'messages', ['user_id'])
    op.create_index('ix_messages_thread_id', 'messages', ['thread_id'])
    op.create_index('ix_messages_user_created', 'messages', ['user_id', 'created_at'])


def downgrade() -> None:
    """Drop messages table and indexes."""

    op.drop_index('ix_messages_user_created', table_name='messages')
    op.drop_index('ix_messages_thread_id', table_name='messages')
    op.drop_index('ix_messages_user_id', table_name='messages')
    op.drop_table('messages')
