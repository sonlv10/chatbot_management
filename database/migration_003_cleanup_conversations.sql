-- Migration: Cleanup conversations table
-- Date: 2025-11-28
-- Purpose: Remove old columns that are now in conversation_messages table

BEGIN;

-- Drop old columns that are no longer used
-- Messages are now stored in conversation_messages table
ALTER TABLE conversations 
DROP COLUMN IF EXISTS user_message,
DROP COLUMN IF EXISTS bot_response,
DROP COLUMN IF EXISTS intent,
DROP COLUMN IF EXISTS confidence,
DROP COLUMN IF EXISTS sender_id;

-- Verify the table structure
COMMENT ON TABLE conversations IS 'Conversation sessions - tracks user chat sessions';
COMMENT ON COLUMN conversations.session_id IS 'Unique session identifier for tracking user conversations';
COMMENT ON COLUMN conversations.message_count IS 'Total number of messages in this conversation (auto-updated by trigger)';
COMMENT ON COLUMN conversations.created_at IS 'Timestamp when conversation started';
COMMENT ON COLUMN conversations.ended_at IS 'Timestamp when conversation ended (NULL if ongoing)';

COMMIT;
