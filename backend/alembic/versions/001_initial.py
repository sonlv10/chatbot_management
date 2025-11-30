"""Initial database schema

Revision ID: 001_initial
Revises: 
Create Date: 2025-11-30 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=True),
    sa.Column('plan', sa.String(length=50), nullable=True, server_default='free'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create bots table
    op.create_table('bots',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('language', sa.String(length=10), nullable=True, server_default='vi'),
    sa.Column('status', sa.String(length=50), nullable=True, server_default='draft'),
    sa.Column('model_path', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bots_id'), 'bots', ['id'], unique=False)

    # Create training_data table
    op.create_table('training_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bot_id', sa.Integer(), nullable=False),
    sa.Column('user_message', sa.Text(), nullable=False),
    sa.Column('bot_response', sa.Text(), nullable=False),
    sa.Column('intent', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_data_id'), 'training_data', ['id'], unique=False)

    # Create conversations table
    op.create_table('conversations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bot_id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.String(length=100), nullable=True),
    sa.Column('message_count', sa.Integer(), nullable=True, server_default='0'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)
    op.create_index(op.f('ix_conversations_session_id'), 'conversations', ['session_id'], unique=True)

    # Create conversation_messages table
    op.create_table('conversation_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('conversation_id', sa.Integer(), nullable=False),
    sa.Column('sender', sa.String(length=10), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('intent', sa.String(length=100), nullable=True),
    sa.Column('confidence', sa.Float(), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_messages_id'), 'conversation_messages', ['id'], unique=False)

    # Create training_sessions table
    op.create_table('training_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bot_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True, server_default='pending'),
    sa.Column('accuracy', sa.Float(), nullable=True),
    sa.Column('vocabulary_size', sa.Integer(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_sessions_id'), 'training_sessions', ['id'], unique=False)

    # Create training_jobs table
    op.create_table('training_jobs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bot_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True, server_default='pending'),
    sa.Column('progress', sa.Integer(), nullable=True, server_default='0'),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('model_path', sa.String(length=500), nullable=True),
    sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('metrics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_jobs_id'), 'training_jobs', ['id'], unique=False)

    # Create training_logs table
    op.create_table('training_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('training_job_id', sa.Integer(), nullable=False),
    sa.Column('log_level', sa.String(length=10), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('source', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['training_job_id'], ['training_jobs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_logs_id'), 'training_logs', ['id'], unique=False)

    # Insert demo user (password: demo123)
    op.execute("""
        INSERT INTO users (email, password_hash, full_name, plan) 
        VALUES (
            'demo@chatbot.com',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lDxgrTnDBS4q',
            'Demo User',
            'free'
        );
    """)


def downgrade() -> None:
    op.drop_table('training_logs')
    op.drop_table('training_jobs')
    op.drop_table('training_sessions')
    op.drop_table('conversation_messages')
    op.drop_table('conversations')
    op.drop_table('training_data')
    op.drop_table('bots')
    op.drop_table('users')
