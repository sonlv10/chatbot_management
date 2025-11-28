"""
Conversation management API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.database import get_db
from app.models import User, Bot, Conversation, ConversationMessage
from app.schemas import (
    ConversationCreate, 
    Conversation as ConversationSchema,
    ConversationWithMessages,
    ConversationHistory,
    ConversationMessage as ConversationMessageSchema
)
from app.auth import get_current_user

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post("/start", response_model=ConversationSchema)
async def start_conversation(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new conversation session"""
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Generate unique session ID
    session_id = f"session_{bot_id}_{uuid.uuid4().hex[:12]}"
    
    # Create conversation
    conversation = Conversation(
        bot_id=bot_id,
        session_id=session_id,
        message_count=0
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation with all messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == conversation.bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return conversation


@router.get("/session/{session_id}", response_model=ConversationWithMessages)
async def get_conversation_by_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation by session ID"""
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == conversation.bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return conversation


@router.post("/{conversation_id}/end")
async def end_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """End a conversation session"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == conversation.bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Mark as ended
    conversation.ended_at = datetime.now()
    db.commit()
    
    return {
        "message": "Conversation ended",
        "conversation_id": conversation_id,
        "message_count": conversation.message_count
    }


@router.get("/bot/{bot_id}/history", response_model=List[ConversationHistory])
async def get_bot_conversation_history(
    bot_id: int,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation history for a bot"""
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Get conversations
    conversations = db.query(Conversation).filter(
        Conversation.bot_id == bot_id
    ).order_by(
        Conversation.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    # Build history response
    history = []
    for conv in conversations:
        # Get first user message as preview
        first_msg = db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conv.id,
            ConversationMessage.sender == 'user'
        ).first()
        
        history.append(ConversationHistory(
            conversation_id=conv.id,
            session_id=conv.session_id,
            message_count=conv.message_count,
            started_at=conv.created_at,
            ended_at=conv.ended_at,
            preview=first_msg.message if first_msg else None
        ))
    
    return history


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == conversation.bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete conversation (cascade will delete messages)
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted successfully"}
