"""
Chat and Training API endpoints
"""
from fastapi import Path, APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Bot, TrainingData, TrainingSession, Conversation
from app.schemas import ChatMessage, ChatResponse, TrainingSession as TrainingSessionSchema
from app.auth import get_current_user
from app.services.rasa_training import RasaTrainingService
from app.services.rasa_service import RasaService
from datetime import datetime

router = APIRouter(prefix="/bots/{bot_id}", tags=["Chat & Training"])

rasa_training = RasaTrainingService()
rasa_service = RasaService()


def train_bot_background(bot_id: int, db: Session):
    """Background task to train bot"""
    # Get training data
    training_data = db.query(TrainingData).filter(
        TrainingData.bot_id == bot_id
    ).all()
    
    if not training_data:
        return
    
    # Get bot
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        return
    
    # Create training session
    session = TrainingSession(
        bot_id=bot_id,
        status='running'
    )
    db.add(session)
    db.commit()
    
    # Update bot status
    bot.status = 'training'
    db.commit()
    
    # Prepare training data
    data_list = [
        {
            'user_message': item.user_message,
            'bot_response': item.bot_response,
            'intent': item.intent
        }
        for item in training_data
    ]
    
    # Train model
    result = rasa_training.prepare_and_train(
        bot_id=bot_id,
        training_data=data_list,
        language=bot.language
    )
    
    # Update session
    session.completed_at = datetime.now()
    
    if result['status'] == 'success':
        session.status = 'completed'
        session.accuracy = result.get('accuracy')
        session.vocabulary_size = result.get('vocabulary_size')
        
        # Update bot
        bot.status = 'active'
        bot.model_path = result.get('model_path')
        
        # Load model into Rasa server
        load_result = rasa_service.load_model(bot_id, result.get('model_path'))
        if load_result['status'] != 'success':
            # Log warning but don't fail the training
            session.error_message = f"Model trained but failed to load: {load_result.get('error_message')}"
    else:
        session.status = 'failed'
        session.error_message = result.get('error_message', 'Unknown error')
        
        # Update bot
        bot.status = 'error'
    
    db.commit()


@router.post("/train", response_model=dict)
def train_bot(
    bot_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger training for bot"""
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Check if training data exists
    data_count = db.query(TrainingData).filter(
        TrainingData.bot_id == bot_id
    ).count()
    
    if data_count == 0:
        raise HTTPException(
            status_code=400,
            detail="No training data available. Please upload training data first."
        )
    
    # Check if already training
    if bot.status == 'training':
        raise HTTPException(
            status_code=400,
            detail="Bot is already training. Please wait."
        )
    
    # Add background task
    background_tasks.add_task(train_bot_background, bot_id, db)
    
    return {
        "message": "Training started in background",
        "bot_id": bot_id,
        "status": "training"
    }


@router.get("/training/sessions", response_model=List[TrainingSessionSchema])
def get_training_sessions(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get training history for bot"""
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    sessions = db.query(TrainingSession).filter(
        TrainingSession.bot_id == bot_id
    ).order_by(TrainingSession.started_at.desc()).all()
    
    return sessions


@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(
    bot_id: int,
    message: ChatMessage,
    session_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with bot - with session tracking and message logging"""
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Check if bot is trained
    if bot.status != 'active' or not bot.model_path:
        raise HTTPException(
            status_code=400,
            detail="Bot is not trained yet. Please train the bot first."
        )
    
    # Get or create conversation session
    conversation = None
    if session_id:
        conversation = db.query(Conversation).filter(
            Conversation.session_id == session_id,
            Conversation.bot_id == bot_id
        ).first()
    
    if not conversation:
        # Create new conversation
        import uuid
        session_id = session_id or f"session_{bot_id}_{uuid.uuid4().hex[:12]}"
        conversation = Conversation(
            bot_id=bot_id,
            session_id=session_id,
            message_count=0
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Ensure correct model is loaded in Rasa
    import time
    t0 = time.time()
    load_result = rasa_service.load_model(bot_id, bot.model_path)
    t1 = time.time()
    print(f"[DEBUG] Load took {t1-t0:.3f}s")
    
    if load_result['status'] == 'error':
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load model: {load_result.get('error_message')}"
        )
    
    # Log user message
    from app.models import ConversationMessage as ConversationMessageModel
    
    user_msg = ConversationMessageModel(
        conversation_id=conversation.id,
        sender='user',
        message=message.message
    )
    db.add(user_msg)
    db.commit()
    
    # Send message to Rasa with session tracking
    t2 = time.time()
    response = rasa_service.chat(
        bot_id=bot_id,
        message=message.message,
        sender_id=session_id  # Use session_id for Rasa tracking
    )
    t3 = time.time()
    print(f"[DEBUG] Chat took {t3-t2:.3f}s")
    
    if response['status'] == 'error':
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with bot: {response.get('error_message')}"
        )
    
    # Log bot response
    bot_msg = ConversationMessageModel(
        conversation_id=conversation.id,
        sender='bot',
        message=response.get('message', ''),
        intent=response.get('intent'),
        confidence=response.get('confidence'),
        extra_data={'entities': response.get('entities', [])}
    )
    db.add(bot_msg)
    db.commit()
    
    return ChatResponse(
        message=response.get('message', 'No response'),
        intent=response.get('intent'),
        confidence=response.get('confidence')
    )


@router.get("/conversations")
def get_conversations(
    bot_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation history"""
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    conversations = db.query(Conversation).filter(
        Conversation.bot_id == bot_id
    ).order_by(Conversation.created_at.desc()).limit(limit).all()
    
    return conversations
