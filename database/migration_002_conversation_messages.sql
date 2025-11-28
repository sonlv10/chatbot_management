-- Migration: Add conversation_messages table for full message tracking
-- Date: 2025-11-25

-- Add session_id and metadata to conversations table
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS session_id VARCHAR(100) UNIQUE;
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS message_count INT DEFAULT 0;
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS ended_at TIMESTAMP;

-- Create conversation_messages table
CREATE TABLE IF NOT EXISTS conversation_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender VARCHAR(10) NOT NULL CHECK (sender IN ('user', 'bot')),
    message TEXT NOT NULL,
    intent VARCHAR(100),
    confidence FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extra_data JSONB
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversation_messages_conversation_id 
    ON conversation_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_timestamp 
    ON conversation_messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_session_id 
    ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_bot_id 
    ON conversations(bot_id);

-- Update message count trigger
CREATE OR REPLACE FUNCTION update_conversation_message_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations 
    SET message_count = message_count + 1
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_message_count ON conversation_messages;
CREATE TRIGGER trigger_update_message_count
    AFTER INSERT ON conversation_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_message_count();

-- Comments
COMMENT ON TABLE conversation_messages IS 'Stores all messages (user and bot) in conversations';
COMMENT ON COLUMN conversation_messages.sender IS 'Either user or bot';
COMMENT ON COLUMN conversation_messages.intent IS 'Detected intent for user messages';
COMMENT ON COLUMN conversation_messages.confidence IS 'Confidence score for intent classification';
COMMENT ON COLUMN conversation_messages.extra_data IS 'Additional data: entities, context, etc.';
