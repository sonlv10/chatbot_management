"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    plan: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Bot schemas
class BotBase(BaseModel):
    name: str
    description: Optional[str] = None
    language: str = 'vi'

class BotCreate(BotBase):
    pass

class BotUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None

class Bot(BotBase):
    id: int
    user_id: int
    status: str
    model_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# Training data schemas
class TrainingDataItem(BaseModel):
    user_message: str
    bot_response: str
    intent: Optional[str] = None

class TrainingDataCreate(TrainingDataItem):
    """Schema for creating or updating a single training data item"""
    pass

class TrainingDataBulkCreate(BaseModel):
    """Schema for bulk creating training data items"""
    data: List[TrainingDataItem]

class TrainingData(TrainingDataItem):
    id: int
    bot_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# Chat schemas
class ChatMessage(BaseModel):
    message: str
    sender_id: Optional[str] = "user"

class ChatResponse(BaseModel):
    message: str
    intent: Optional[str] = None
    confidence: Optional[float] = None

# Training session schemas
class TrainingSession(BaseModel):
    id: int
    bot_id: int
    status: str
    accuracy: Optional[float] = None
    vocabulary_size: Optional[int] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# Conversation schemas
class ConversationMessageBase(BaseModel):
    sender: str
    message: str
    intent: Optional[str] = None
    confidence: Optional[float] = None

class ConversationMessage(ConversationMessageBase):
    id: int
    conversation_id: int
    timestamp: datetime
    extra_data: Optional[dict] = None
    
    class Config:
        orm_mode = True

class ConversationBase(BaseModel):
    session_id: str

class ConversationCreate(ConversationBase):
    bot_id: int

class Conversation(ConversationBase):
    id: int
    bot_id: int
    message_count: int
    created_at: datetime
    ended_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class ConversationWithMessages(Conversation):
    messages: List[ConversationMessage] = []
    
    class Config:
        orm_mode = True

class ConversationHistory(BaseModel):
    conversation_id: int
    session_id: str
    message_count: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    preview: Optional[str] = None  # First user message

# Training job schemas
class TrainingJobBase(BaseModel):
    config: Optional[dict] = None


class TrainingJobCreate(TrainingJobBase):
    """Schema for creating a new training job"""
    pass


class TrainingJobUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None
    model_path: Optional[str] = None
    metrics: Optional[dict] = None
    error_message: Optional[str] = None


class TrainingJobResponse(TrainingJobBase):
    """Schema for training job response"""
    id: int
    bot_id: int
    status: str  # pending, running, completed, failed, cancelled
    progress: int  # 0-100
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    model_path: Optional[str] = None
    metrics: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# Training log schemas
class TrainingLogBase(BaseModel):
    log_level: str
    message: str
    source: Optional[str] = None


class TrainingLogCreate(TrainingLogBase):
    training_job_id: int


class TrainingLogResponse(TrainingLogBase):
    """Schema for training log entry"""
    id: int
    training_job_id: int
    timestamp: datetime
    
    class Config:
        orm_mode = True


class TrainingJobWithLogs(TrainingJobResponse):
    """Schema for training job including logs"""
    logs: List[TrainingLogResponse] = []
    
    class Config:
        orm_mode = True
