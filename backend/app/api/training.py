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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all training data for a bot"""
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    training_data = db.query(TrainingData).filter(
        TrainingData.bot_id == bot_id
    ).all()
    
    return training_data

@router.post("/", response_model=dict)
def add_training_data(
    bot_id: int,
    training_data: TrainingDataCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add training data to bot"""
    # Verify bot ownership
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Add training data
    added_count = 0
    for item in training_data.data:
        db_data = TrainingData(
            bot_id=bot_id,
            user_message=item.user_message,
            bot_response=item.bot_response,
            intent=item.intent
        )
        db.add(db_data)
        added_count += 1
    
    db.commit()
    
    return {
        "message": "Training data added successfully",
        "count": added_count
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
