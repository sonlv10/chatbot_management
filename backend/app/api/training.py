"""
Training data management API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.models import User, Bot, TrainingData
from app.schemas import TrainingData as TrainingDataSchema, TrainingDataCreate
from app.auth import get_current_user
from app.utils.data_parsers import TrainingDataParser

router = APIRouter(prefix="/bots/{bot_id}/training", tags=["Training Data"])

@router.get("/", response_model=List[TrainingDataSchema])
def get_training_data(
    bot_id: int,
    user_message: str = None,
    bot_response: str = None,
    intent: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all training data for a bot with server-side filtering and sorting
    
    Args:
        bot_id: Bot ID
        user_message: Search text in user_message
        bot_response: Search text in bot_response
        intent: Filter by specific intent
        sort_by: Field to sort by (user_message, bot_response, intent, created_at)
        sort_order: Sort order (asc or desc)
    """
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Build query
    query = db.query(TrainingData).filter(TrainingData.bot_id == bot_id)
    
    # Apply search filters
    if user_message:
        user_message_filter = f"%{user_message.lower()}%"
        query = query.filter(TrainingData.user_message.ilike(user_message_filter))
    
    if bot_response:
        bot_response_filter = f"%{bot_response.lower()}%"
        query = query.filter(TrainingData.bot_response.ilike(bot_response_filter))
    
    # Apply intent filter
    if intent:
        query = query.filter(TrainingData.intent == intent)
    
    # Apply sorting
    valid_sort_fields = {
        'user_message': TrainingData.user_message,
        'bot_response': TrainingData.bot_response,
        'intent': TrainingData.intent,
        'created_at': TrainingData.created_at
    }
    
    sort_field = valid_sort_fields.get(sort_by, TrainingData.created_at)
    
    if sort_order.lower() == 'asc':
        query = query.order_by(sort_field.asc())
    else:
        query = query.order_by(sort_field.desc())
    
    training_data = query.all()
    
    return training_data

@router.post("/", response_model=TrainingDataSchema)
def add_training_data(
    bot_id: int,
    training_data: TrainingDataCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add single training data item to bot"""
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Add training data
    db_data = TrainingData(
        bot_id=bot_id,
        user_message=training_data.user_message,
        bot_response=training_data.bot_response,
        intent=training_data.intent
    )
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    
    return db_data

@router.put("/{data_id}", response_model=TrainingDataSchema)
def update_training_data(
    bot_id: int,
    data_id: int,
    training_data: TrainingDataCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update training data item"""
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Get and update data
    db_data = db.query(TrainingData).filter(
        TrainingData.id == data_id,
        TrainingData.bot_id == bot_id
    ).first()
    
    if not db_data:
        raise HTTPException(status_code=404, detail="Training data not found")
    
    db_data.user_message = training_data.user_message
    db_data.bot_response = training_data.bot_response
    db_data.intent = training_data.intent
    
    db.commit()
    db.refresh(db_data)
    
    return db_data

@router.post("/parse", response_model=dict)
async def parse_training_file(
    bot_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Parse training data file and return preview without saving
    Supported: JSON, CSV, YAML, TXT, Markdown
    """
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Read file
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    # Parse file using format-specific parser
    try:
        parsed_data = TrainingDataParser.parse(file.filename, content_str)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
    
    if not parsed_data:
        raise HTTPException(
            status_code=400,
            detail="No valid training data found in file"
        )
    
    return {
        "message": "File parsed successfully",
        "count": len(parsed_data),
        "data": parsed_data
    }

@router.post("/upload", response_model=dict)
async def upload_training_file(
    bot_id: int,
    file: UploadFile = File(...),
    use_intelligent_classification: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload training data from multiple formats
    Supported: JSON, CSV, YAML, TXT, Markdown
    
    Args:
        use_intelligent_classification: If True, use Rasa NLU to classify unknown intents
    """
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Read file
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    # Parse file using format-specific parser
    try:
        parsed_data = TrainingDataParser.parse(file.filename, content_str)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
    
    if not parsed_data:
        raise HTTPException(
            status_code=400,
            detail="No valid training data found in file"
        )
    
    # Enhance with intelligent classification if requested
    if use_intelligent_classification:
        try:
            parsed_data = TrainingDataParser.enhance_with_intelligent_classification(
                parsed_data, 
                bot_id
            )
        except Exception as e:
            # Log error but continue with original data
            import logging
            logging.warning(f"Intelligent classification failed: {str(e)}")
    
    # Add training data
    added_count = 0
    for item in parsed_data:
        db_data = TrainingData(
            bot_id=bot_id,
            user_message=item["user"],
            bot_response=item["bot"],
            intent=item.get("intent")
        )
        db.add(db_data)
        added_count += 1
    
    db.commit()
    
    return {
        "message": "Training data uploaded successfully",
        "count": added_count
    }

@router.delete("/{data_id}", status_code=204)
def delete_training_data(
    bot_id: int,
    data_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete training data item"""
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Delete data
    data = db.query(TrainingData).filter(
        TrainingData.id == data_id,
        TrainingData.bot_id == bot_id
    ).first()
    
    if not data:
        raise HTTPException(status_code=404, detail="Training data not found")
    
    db.delete(data)
    db.commit()
    return None
