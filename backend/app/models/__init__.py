"""
Database models
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    plan = Column(String(50), default='free')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    bots = relationship("Bot", back_populates="user", cascade="all, delete-orphan")


class Bot(Base):
    __tablename__ = "bots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    language = Column(String(10), default='vi')
    status = Column(String(50), default='draft')  # draft, training, active, error
    model_path = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="bots")
    training_data = relationship("TrainingData", back_populates="bot", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="bot", cascade="all, delete-orphan")
    training_sessions = relationship("TrainingSession", back_populates="bot", cascade="all, delete-orphan")


class TrainingData(Base):
    __tablename__ = "training_data"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    intent = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    bot = relationship("Bot", back_populates="training_data")


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(100), unique=True, index=True)
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    
    bot = relationship("Bot", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(10), nullable=False)  # 'user' or 'bot'
    message = Column(Text, nullable=False)
    intent = Column(String(100))
    confidence = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    extra_data = Column(JSON)  # Changed from 'metadata' to 'extra_data'
    
    conversation = relationship("Conversation", back_populates="messages")


class TrainingSession(Base):
    __tablename__ = "training_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default='pending')  # pending, running, completed, failed
    accuracy = Column(Float)
    vocabulary_size = Column(Integer)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    bot = relationship("Bot", back_populates="training_sessions")


class TrainingJob(Base):
    __tablename__ = "training_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default='pending')  # pending, running, completed, failed, cancelled
    progress = Column(Integer, default=0)  # 0-100
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    model_path = Column(String(500))
    config = Column(JSON)  # training configuration
    metrics = Column(JSON)  # training metrics (accuracy, f1-score, etc.)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    bot = relationship("Bot")
    logs = relationship("TrainingLog", back_populates="training_job", cascade="all, delete-orphan")


class TrainingLog(Base):
    __tablename__ = "training_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    training_job_id = Column(Integer, ForeignKey("training_jobs.id", ondelete="CASCADE"), nullable=False)
    log_level = Column(String(10), nullable=False)  # DEBUG, INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String(50))  # stdout, stderr, rasa, custom
    
    training_job = relationship("TrainingJob", back_populates="logs")
