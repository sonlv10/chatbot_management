"""
Bot management API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
import shutil

from app.database import get_db
from app.models import User, Bot
from app.schemas import Bot as BotSchema, BotCreate, BotUpdate
from app.auth import get_current_user

router = APIRouter(prefix="/bots", tags=["Bots"])

@router.get("/", response_model=List[BotSchema])
def get_user_bots(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all bots for current user"""
    bots = db.query(Bot).filter(Bot.user_id == current_user.id).all()
    return bots

@router.post("/", response_model=BotSchema, status_code=status.HTTP_201_CREATED)
def create_bot(
    bot: BotCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new bot"""
    db_bot = Bot(
        user_id=current_user.id,
        name=bot.name,
        description=bot.description,
        language=bot.language
    )
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

@router.get("/{bot_id}", response_model=BotSchema)
def get_bot(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get bot by ID"""
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return bot

@router.put("/{bot_id}", response_model=BotSchema)
def update_bot(
    bot_id: int,
    bot_update: BotUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update bot"""
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Update fields
    if bot_update.name is not None:
        bot.name = bot_update.name
    if bot_update.description is not None:
        bot.description = bot_update.description
    if bot_update.language is not None:
        bot.language = bot_update.language
    
    db.commit()
    db.refresh(bot)
    return bot

@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bot(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete bot and its associated model files"""
    bot = db.query(Bot).filter(
        Bot.id == bot_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Delete bot from database
    db.delete(bot)
    db.commit()
    
    # Check if this was the last bot for the user
    remaining_bots = db.query(Bot).filter(Bot.user_id == current_user.id).count()
    
    # If no bots remain for this user, check if there are any bots at all
    if remaining_bots == 0:
        total_bots = db.query(Bot).count()
        if total_bots == 0:
            # Reset the bot ID sequence to 1
            try:
                db.execute(text("ALTER SEQUENCE bots_id_seq RESTART WITH 1"))
                db.commit()
                print("Reset bot ID sequence to 1")
            except Exception as e:
                print(f"Warning: Failed to reset bot ID sequence: {str(e)}")
    
    # Delete bot's model directory
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        bot_dir = os.path.join(project_root, "rasa", "models", f"bot_{bot_id}")
        
        if os.path.exists(bot_dir):
            shutil.rmtree(bot_dir)
            print(f"Deleted model directory: {bot_dir}")
    except Exception as e:
        # Log the error but don't fail the delete operation
        print(f"Warning: Failed to delete model directory for bot {bot_id}: {str(e)}")
    
    return None
