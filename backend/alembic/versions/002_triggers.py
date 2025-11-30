"""Add triggers and functions for conversation tracking

Revision ID: 002_triggers
Revises: 001_initial
Create Date: 2025-11-30 10:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_triggers'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create function to update conversation message count
    op.execute("""
        CREATE OR REPLACE FUNCTION update_conversation_message_count()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE conversations 
            SET message_count = message_count + 1
            WHERE id = NEW.conversation_id;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger for message count updates
    op.execute("""
        CREATE TRIGGER trigger_update_message_count
        AFTER INSERT ON conversation_messages
        FOR EACH ROW
        EXECUTE FUNCTION update_conversation_message_count();
    """)

    # Create function to update training_jobs updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_training_jobs_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger for training_jobs updated_at
    op.execute("""
        CREATE TRIGGER training_jobs_updated_at_trigger
        BEFORE UPDATE ON training_jobs
        FOR EACH ROW
        EXECUTE FUNCTION update_training_jobs_updated_at();
    """)

    # Add comments for documentation
    op.execute("COMMENT ON TABLE conversations IS 'Conversation sessions - tracks user chat sessions'")
    op.execute("COMMENT ON COLUMN conversations.session_id IS 'Unique session identifier for tracking user conversations'")
    op.execute("COMMENT ON COLUMN conversations.message_count IS 'Total number of messages in this conversation (auto-updated by trigger)'")
    op.execute("COMMENT ON COLUMN conversations.created_at IS 'Timestamp when conversation started'")
    op.execute("COMMENT ON COLUMN conversations.ended_at IS 'Timestamp when conversation ended (NULL if ongoing)'")
    
    op.execute("COMMENT ON TABLE conversation_messages IS 'Stores all messages (user and bot) in conversations'")
    op.execute("COMMENT ON COLUMN conversation_messages.sender IS 'Either user or bot'")
    op.execute("COMMENT ON COLUMN conversation_messages.intent IS 'Detected intent for user messages'")
    op.execute("COMMENT ON COLUMN conversation_messages.confidence IS 'Confidence score for intent classification'")
    op.execute("COMMENT ON COLUMN conversation_messages.extra_data IS 'Additional data: entities, context, etc.'")
    
    op.execute("COMMENT ON TABLE training_jobs IS 'Tracks Rasa model training jobs with status and progress'")
    op.execute("COMMENT ON TABLE training_logs IS 'Stores logs generated during training process'")
    op.execute("COMMENT ON COLUMN training_jobs.status IS 'Job status: pending, running, completed, failed, cancelled'")
    op.execute("COMMENT ON COLUMN training_jobs.progress IS 'Training progress percentage (0-100)'")
    op.execute("COMMENT ON COLUMN training_jobs.config IS 'Training configuration in JSON format'")
    op.execute("COMMENT ON COLUMN training_jobs.metrics IS 'Training results metrics (accuracy, f1, etc.)'")


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS training_jobs_updated_at_trigger ON training_jobs")
    op.execute("DROP TRIGGER IF EXISTS trigger_update_message_count ON conversation_messages")
    
    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS update_training_jobs_updated_at()")
    op.execute("DROP FUNCTION IF EXISTS update_conversation_message_count()")
