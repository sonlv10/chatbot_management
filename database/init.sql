-- Database initialization for Chatbot Management Platform

-- Create database
CREATE DATABASE chatbot_db;

-- Connect to database
\c chatbot_db;

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    plan VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Bots table
CREATE TABLE bots (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    language VARCHAR(10) DEFAULT 'vi',
    status VARCHAR(50) DEFAULT 'draft',
    model_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Training data table
CREATE TABLE training_data (
    id SERIAL PRIMARY KEY,
    bot_id INTEGER REFERENCES bots(id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    intent VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    bot_id INTEGER REFERENCES bots(id) ON DELETE CASCADE,
    sender_id VARCHAR(255),
    user_message TEXT NOT NULL,
    bot_response TEXT,
    intent VARCHAR(100),
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Training sessions
CREATE TABLE training_sessions (
    id SERIAL PRIMARY KEY,
    bot_id INTEGER REFERENCES bots(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    accuracy FLOAT,
    vocabulary_size INTEGER,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_bots_user_id ON bots(user_id);
CREATE INDEX idx_training_data_bot_id ON training_data(bot_id);
CREATE INDEX idx_conversations_bot_id ON conversations(bot_id);
CREATE INDEX idx_training_sessions_bot_id ON training_sessions(bot_id);

-- Demo user (password: demo123)
INSERT INTO users (email, password_hash, full_name, plan) 
VALUES (
    'demo@chatbot.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lDxgrTnDBS4q',
    'Demo User',
    'free'
);
