"""
API endpoints for training jobs and progress tracking
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime
import asyncio
import subprocess
import os
import re

from ..database import get_db
from ..auth import get_current_user
from ..schemas import User, TrainingJobResponse, TrainingJobCreate, TrainingJobWithLogs, TrainingLogResponse

router = APIRouter()

# In-memory store for active training processes
active_training_jobs = {}

def parse_rasa_log_level(line: str) -> str:
    """Extract log level from Rasa output"""
    if "ERROR" in line or "Exception" in line or "Traceback" in line:
        return "ERROR"
    elif "WARNING" in line or "WARN" in line:
        return "WARNING"
    elif "DEBUG" in line:
        return "DEBUG"
    else:
        return "INFO"

def run_rasa_training(job_id: int, bot_id: int, db_connection_string: str):
    """
    Background task to run Rasa training and capture logs
    """
    conn = None
    try:
        # Import psycopg2 for direct DB connection in background task
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(db_connection_string)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Update job status to running and set started_at
        cursor.execute(
            "UPDATE training_jobs SET status = 'running', progress = 0, started_at = NOW() WHERE id = %s",
            (job_id,)
        )
        conn.commit()
        
        # Create bot-specific training directory in rasa/models
        # Get project root directory (backend/../rasa/models)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        bot_dir = os.path.join(project_root, "rasa", "models", f"bot_{bot_id}")
        os.makedirs(bot_dir, exist_ok=True)
        
        # Export training data from database to NLU format
        cursor.execute(
            "SELECT user_message, bot_response, intent FROM training_data WHERE bot_id = %s",
            (bot_id,)
        )
        training_data = cursor.fetchall()
        
        if not training_data:
            raise Exception("No training data found for this bot")
        
        data_count = len(training_data)
        
        # Update progress - Data loaded (5%)
        cursor.execute(
            "UPDATE training_jobs SET progress = 5 WHERE id = %s",
            (job_id,)
        )
        conn.commit()
        
        cursor.execute(
            "INSERT INTO training_logs (training_job_id, log_level, message) VALUES (%s, %s, %s)",
            (job_id, "INFO", f"📊 Loaded {data_count} training examples")
        )
        conn.commit()
        
        # Generate NLU data in YAML format with entities
        nlu_content = "version: \"3.1\"\n\nnlu:\n"
        current_intent = None
        
        # First pass: collect all examples by intent
        intent_examples = {}
        for item in training_data:
            intent = item['intent'] or 'unknown'
            if intent not in intent_examples:
                intent_examples[intent] = []
            intent_examples[intent].append(item['user_message'])
        
        # Second pass: write NLU with entity annotations
        for intent, examples in intent_examples.items():
            nlu_content += f"\n- intent: {intent}\n  examples: |\n"
            for example in examples:
                # Try to detect and annotate entities automatically
                annotated_example = example
                
                # Simple entity detection patterns (can be enhanced)
                import re
                
                # Phone number pattern
                phone_pattern = r'(\d{10,11}|\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'
                if re.search(phone_pattern, example):
                    annotated_example = re.sub(phone_pattern, r'[\1](phone_number)', annotated_example)
                
                # Email pattern
                email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                if re.search(email_pattern, example):
                    annotated_example = re.sub(email_pattern, r'[\1](email)', annotated_example)
                
                nlu_content += f"    - {annotated_example}\n"
        
        # Add lookup tables for common entities
        nlu_content += """
- lookup: product_name
  examples: |
    - áo
    - quần
    - giày
    - túi
    - mũ
    - váy
    - đồng hồ
    - điện thoại
    - laptop
    - máy tính

- lookup: location
  examples: |
    - Hà Nội
    - Hồ Chí Minh
    - Đà Nẵng
    - Hải Phòng
    - Cần Thơ
    - Nha Trang
    - Huế
    - Vũng Tàu
"""
        
        # Write NLU file
        nlu_file = os.path.join(bot_dir, "data", "nlu.yml")
        os.makedirs(os.path.dirname(nlu_file), exist_ok=True)
        with open(nlu_file, "w", encoding="utf-8") as f:
            f.write(nlu_content)
        
        # Update progress - NLU file created (10%)
        cursor.execute(
            "UPDATE training_jobs SET progress = 10 WHERE id = %s",
            (job_id,)
        )
        conn.commit()
        
        cursor.execute(
            "INSERT INTO training_logs (training_job_id, log_level, message) VALUES (%s, %s, %s)",
            (job_id, "INFO", f"✏️ Generated NLU training file")
        )
        conn.commit()
        
        # Create enhanced config.yml with entity extraction and better context handling
        config_content = """
language: vi
pipeline:
  - name: WhitespaceTokenizer
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 4
  - name: DIETClassifier
    epochs: 100
    constrain_similarities: true
    entity_recognition: true
    use_masked_language_model: true
  - name: EntitySynonymMapper
  - name: ResponseSelector
    epochs: 100
  - name: FallbackClassifier
    threshold: 0.3

policies:
  - name: MemoizationPolicy
    max_history: 5
  - name: TEDPolicy
    max_history: 5
    epochs: 100
    constrain_similarities: true
  - name: RulePolicy
    core_fallback_threshold: 0.2
    core_fallback_action_name: "action_default_fallback"
  - name: UnexpecTEDIntentPolicy
    max_history: 5
    epochs: 100
"""
        config_file = os.path.join(bot_dir, "config.yml")
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config_content)
        
        # Create minimal domain.yml with responses for each intent
        intents = list(set([item['intent'] or 'unknown' for item in training_data]))
        
        # Group responses by intent
        intent_responses = {}
        for item in training_data:
            intent = item['intent'] or 'unknown'
            if intent not in intent_responses:
                intent_responses[intent] = []
            response_text = item['bot_response']
            if response_text and response_text not in [r['text'] for r in intent_responses[intent]]:
                intent_responses[intent].append({'text': response_text})
        
        # Build responses section
        responses_content = ""
        for intent in intents:
            responses_content += f"  utter_{intent}:\n"
            if intent in intent_responses and intent_responses[intent]:
                for response in intent_responses[intent]:
                    responses_content += f"    - text: \"{response['text']}\"\n"
            else:
                responses_content += f"    - text: \"Xin lỗi, tôi chưa có câu trả lời cho {intent}.\"\n"
        
        # Create slots for context memory
        slots_content = """
slots:
  user_name:
    type: text
    influence_conversation: true
    mappings:
      - type: from_entity
        entity: user_name
  
  product_name:
    type: text
    influence_conversation: true
    mappings:
      - type: from_entity
        entity: product_name
  
  location:
    type: text
    influence_conversation: true
    mappings:
      - type: from_entity
        entity: location
  
  phone_number:
    type: text
    influence_conversation: true
    mappings:
      - type: from_entity
        entity: phone_number
  
  email:
    type: text
    influence_conversation: true
    mappings:
      - type: from_entity
        entity: email
  
  previous_intent:
    type: text
    influence_conversation: true
    mappings:
      - type: custom
  
  context_info:
    type: any
    influence_conversation: false
    mappings:
      - type: custom
"""
        
        # Create entities list
        entities_content = """
entities:
  - user_name
  - product_name
  - location
  - phone_number
  - email
"""
        
        domain_content = f"""version: "3.1"

intents:
{chr(10).join(f'  - {intent}' for intent in intents)}

{entities_content}
{slots_content}

responses:
{responses_content}
  utter_default:
    - text: "Xin lỗi, tôi chưa hiểu câu hỏi của bạn."
"""
        domain_file = os.path.join(bot_dir, "domain.yml")
        with open(domain_file, "w", encoding="utf-8") as f:
            f.write(domain_content)
        
        # Create rules.yml to map intents to responses
        rules_content = """version: "3.1"

rules:
"""
        for intent in intents:
            rules_content += f"""
- rule: Respond to {intent}
  steps:
    - intent: {intent}
    - action: utter_{intent}
"""
        
        rules_file = os.path.join(bot_dir, "data", "rules.yml")
        with open(rules_file, "w", encoding="utf-8") as f:
            f.write(rules_content)
        
        # Create stories.yml for conversation flows with context
        stories_content = """version: "3.1"

stories:
"""
        # Generate basic stories from training data
        # Group by intent to create conversation patterns
        intent_groups = {}
        for item in training_data:
            intent = item['intent'] or 'unknown'
            if intent not in intent_groups:
                intent_groups[intent] = []
            intent_groups[intent].append(item)
        
        # Create multi-turn conversation stories
        story_id = 1
        for intent, items in intent_groups.items():
            if len(items) > 0:
                stories_content += f"""
- story: conversation_{story_id}_{intent}
  steps:
    - intent: {intent}
    - action: utter_{intent}
"""
                story_id += 1
        
        # Add context-aware stories
        if len(intents) > 1:
            # Create stories where one intent follows another
            intent_list = list(intents)
            for i in range(min(3, len(intent_list)-1)):  # Create a few multi-turn stories
                stories_content += f"""
- story: multi_turn_{i+1}
  steps:
    - intent: {intent_list[i]}
    - action: utter_{intent_list[i]}
    - intent: {intent_list[i+1]}
    - action: utter_{intent_list[i+1]}
"""
        
        stories_file = os.path.join(bot_dir, "data", "stories.yml")
        with open(stories_file, "w", encoding="utf-8") as f:
            f.write(stories_content)
        
        # Update progress - Configuration ready (15%)
        cursor.execute(
            "UPDATE training_jobs SET progress = 15 WHERE id = %s",
            (job_id,)
        )
        conn.commit()
        
        cursor.execute(
            "INSERT INTO training_logs (training_job_id, log_level, message) VALUES (%s, %s, %s)",
            (job_id, "INFO", f"⚙️ Configuration files ready ({len(intents)} intents)")
        )
        conn.commit()
        
        # Log that training is starting
        cursor.execute(
            "INSERT INTO training_logs (training_job_id, log_level, message) VALUES (%s, %s, %s)",
            (job_id, "INFO", f"Starting Rasa training for bot {bot_id}...")
        )
        conn.commit()
        
        # Run Rasa training
        process = subprocess.Popen(
            ["rasa", "train", "--domain", domain_file, "--config", config_file, 
             "--data", os.path.join(bot_dir, "data"), "--out", bot_dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=bot_dir,
            universal_newlines=True,
            bufsize=1
        )
        
        # Store process in active jobs
        active_training_jobs[job_id] = process
        
        # Update progress - Training started (20%)
        cursor.execute(
            "UPDATE training_jobs SET progress = 20 WHERE id = %s",
            (job_id,)
        )
        conn.commit()
        
        # Stream logs and update progress
        progress = 20
        total_epochs = 100  # Default from config
        last_progress = 20
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            
            line = line.strip()
            if line:
                log_level = parse_rasa_log_level(line)
                
                # Insert log into database
                cursor.execute(
                    "INSERT INTO training_logs (training_job_id, log_level, message) VALUES (%s, %s, %s)",
                    (job_id, log_level, line)
                )
                conn.commit()
                
                # Update progress based on log content
                if "Epoch" in line:
                    # Extract epoch number to estimate progress
                    match = re.search(r"Epoch (\d+)/(\d+)", line)
                    if match:
                        current_epoch = int(match.group(1))
                        total_epochs = int(match.group(2))
                        # Progress from 20% to 85% based on epochs (65% range for training)
                        progress = 20 + int((current_epoch / total_epochs) * 65)
                        
                        # Only update if progress increased by at least 2% to reduce DB writes
                        if progress >= last_progress + 2 or progress >= 85:
                            cursor.execute(
                                "UPDATE training_jobs SET progress = %s WHERE id = %s",
                                (min(progress, 85), job_id)
                            )
                            conn.commit()
                            last_progress = progress
                elif "Finished training" in line or "Training completed" in line:
                    progress = 90
                    cursor.execute(
                        "UPDATE training_jobs SET progress = %s WHERE id = %s",
                        (progress, job_id)
                    )
                    conn.commit()
                    last_progress = progress
                elif "Your Rasa model is trained" in line or "Model training completed" in line:
                    progress = 95
                    cursor.execute(
                        "UPDATE training_jobs SET progress = %s WHERE id = %s",
                        (progress, job_id)
                    )
                    conn.commit()
                    last_progress = progress
        
        process.wait()
        
        # Check if training was successful
        if process.returncode == 0:
            # Find the generated model file (get the newest one)
            model_files = [f for f in os.listdir(bot_dir) if f.endswith('.tar.gz')]
            if model_files:
                # Sort by modification time, newest first
                model_files.sort(key=lambda f: os.path.getmtime(os.path.join(bot_dir, f)), reverse=True)
                newest_model = model_files[0]
                model_path = os.path.join(bot_dir, newest_model)
                
                # Delete old model files (keep only the newest one)
                if len(model_files) > 1:
                    deleted_count = 0
                    for old_model in model_files[1:]:
                        try:
                            old_model_path = os.path.join(bot_dir, old_model)
                            os.remove(old_model_path)
                            deleted_count += 1
                        except Exception as e:
                            cursor.execute(
                                "INSERT INTO training_logs (training_job_id, log_level, message) VALUES (%s, %s, %s)",
                                (job_id, "WARNING", f"Could not delete old model {old_model}: {str(e)}")
                            )
                            conn.commit()
                    
                    if deleted_count > 0:
                        cursor.execute(
                            "INSERT INTO training_logs (training_job_id, log_level, message) VALUES (%s, %s, %s)",
                            (job_id, "INFO", f"🗑️ Cleaned up {deleted_count} old model file(s)")
                        )
                        conn.commit()
                
                # Calculate duration
                cursor.execute(
                    "SELECT started_at FROM training_jobs WHERE id = %s",
                    (job_id,)
                )
                started_at = cursor.fetchone()['started_at']
                # Make datetime timezone-aware to match database timestamp
                from datetime import timezone
                now = datetime.now(timezone.utc)
                
                # If started_at is timezone-naive, make it timezone-aware (assuming UTC)
                if started_at.tzinfo is None:
                    started_at = started_at.replace(tzinfo=timezone.utc)
                
                duration = int((now - started_at).total_seconds())
                
                # Update job as completed
                cursor.execute(
                    """UPDATE training_jobs 
                       SET status = 'completed', progress = 100, model_path = %s, 
                           completed_at = NOW() 
                       WHERE id = %s""",
                    (model_path, job_id)
                )
                
                # Update bot model_path
                cursor.execute(
                    "UPDATE bots SET model_path = %s, status = 'trained' WHERE id = %s",
                    (model_path, bot_id)
                )
                
                cursor.execute(
                    "INSERT INTO training_logs (training_job_id, log_level, message) VALUES (%s, %s, %s)",
                    (job_id, "INFO", f"✅ Training completed successfully! Model saved to {model_path}")
                )
                conn.commit()
            else:
                raise Exception("Training completed but no model file was generated")
        else:
            raise Exception(f"Training process failed with exit code {process.returncode}")
            
    except Exception as e:
        error_msg = str(e)
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE training_jobs 
                   SET status = 'failed', error_message = %s, completed_at = NOW() 
                   WHERE id = %s""",
                (error_msg, job_id)
            )
            cursor.execute(
                "INSERT INTO training_logs (training_job_id, log_level, message) VALUES (%s, %s, %s)",
                (job_id, "ERROR", f"❌ Training failed: {error_msg}")
            )
            conn.commit()
    finally:
        if job_id in active_training_jobs:
            del active_training_jobs[job_id]
        if conn:
            conn.close()

@router.post("/bots/{bot_id}/train", response_model=TrainingJobResponse)
async def start_training(
    bot_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Start a new Rasa training job for the specified bot
    """
    print(f"[DEBUG] start_training called for bot_id={bot_id}, user={current_user.id}")
    
    # Check if bot exists and belongs to user
    result = db.execute(
        text("SELECT id FROM bots WHERE id = :bot_id AND user_id = :user_id"),
        {"bot_id": bot_id, "user_id": current_user.id}
    )
    bot = result.fetchone()
    
    if not bot:
        print(f"[DEBUG] Bot {bot_id} not found for user {current_user.id}")
        raise HTTPException(status_code=404, detail="Bot not found")
    
    print(f"[DEBUG] Bot found: {bot}")
    
    # Check if there's already a running job for this bot
    result = db.execute(
        text("SELECT id FROM training_jobs WHERE bot_id = :bot_id AND status IN ('pending', 'running')"),
        {"bot_id": bot_id}
    )
    active_job = result.fetchone()
    
    if active_job:
        print(f"[DEBUG] Active job found: {active_job}")
        raise HTTPException(
            status_code=400, 
            detail="A training job is already running for this bot"
        )
    
    print(f"[DEBUG] No active job, creating new one...")
    
    # Create new training job
    result = db.execute(
        text("""
            INSERT INTO training_jobs (bot_id, status, progress) 
            VALUES (:bot_id, 'pending', 0) 
            RETURNING id, bot_id, status, progress, model_path, error_message, 
                      started_at, completed_at, created_at, updated_at
        """),
        {"bot_id": bot_id}
    )
    
    print(f"[DEBUG] INSERT executed, committing...")
    db.commit()
    
    job = result.fetchone()
    print(f"[DEBUG] Created training job: {job}")
    
    # Get database connection string from environment
    import os
    db_url = os.getenv("DATABASE_URL", "postgresql://chatbot_user:chatbot_pass@localhost:5432/chatbot_db")
    
    # Start training in background
    background_tasks.add_task(run_rasa_training, job.id, bot_id, db_url)
    
    print(f"[DEBUG] Returning job response: {dict(job)}")
    return TrainingJobResponse(**dict(job))

@router.get("/bots/{bot_id}/training-jobs", response_model=List[TrainingJobResponse])
async def get_training_jobs(
    bot_id: int,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get training job history for a bot
    """
    # Verify bot belongs to user
    result = db.execute(
        text("SELECT id FROM bots WHERE id = :bot_id AND user_id = :user_id"),
        {"bot_id": bot_id, "user_id": current_user.id}
    )
    bot = result.fetchone()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Get training jobs
    result = db.execute(
        text("""
            SELECT id, bot_id, status, progress, model_path, error_message, 
                   started_at, completed_at, created_at, updated_at
            FROM training_jobs 
            WHERE bot_id = :bot_id 
            ORDER BY created_at DESC 
            LIMIT :limit
        """),
        {"bot_id": bot_id, "limit": limit}
    )
    
    jobs = result.fetchall()
    return [TrainingJobResponse(**dict(job)) for job in jobs]

@router.get("/training-jobs/{job_id}", response_model=TrainingJobWithLogs)
async def get_training_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get detailed information about a specific training job including logs
    """
    # Get job details and verify it belongs to user's bot
    result = db.execute(
        text("""
            SELECT tj.id, tj.bot_id, tj.status, tj.progress, tj.model_path, 
                   tj.error_message, tj.started_at, tj.completed_at, 
                   tj.created_at, tj.updated_at
            FROM training_jobs tj
            JOIN bots b ON tj.bot_id = b.id
            WHERE tj.id = :job_id AND b.user_id = :user_id
        """),
        {"job_id": job_id, "user_id": current_user.id}
    )
    
    job = result.fetchone()
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    # Get logs for this job
    result = db.execute(
        text("""
            SELECT id, training_job_id, log_level, message, timestamp
            FROM training_logs 
            WHERE training_job_id = :job_id 
            ORDER BY timestamp ASC
        """),
        {"job_id": job_id}
    )
    
    logs = result.fetchall()
    
    job_dict = dict(job)
    job_dict['logs'] = [TrainingLogResponse(**dict(log)) for log in logs]
    
    return TrainingJobWithLogs(**job_dict)

@router.get("/training-jobs/{job_id}/logs", response_model=List[TrainingLogResponse])
async def get_training_logs(
    job_id: int,
    limit: int = 100,
    offset: int = 0,
    log_level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get logs for a specific training job with pagination
    """
    # Verify job belongs to user's bot
    result = db.execute(
        text("""
            SELECT tj.id
            FROM training_jobs tj
            JOIN bots b ON tj.bot_id = b.id
            WHERE tj.id = :job_id AND b.user_id = :user_id
        """),
        {"job_id": job_id, "user_id": current_user.id}
    )
    
    job = result.fetchone()
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    # Build query with optional log_level filter
    query = """
        SELECT id, training_job_id, log_level, message, timestamp
        FROM training_logs 
        WHERE training_job_id = :job_id
    """
    params = {"job_id": job_id, "limit": limit, "offset": offset}
    
    if log_level:
        query += " AND log_level = :log_level"
        params["log_level"] = log_level
    
    query += " ORDER BY timestamp ASC LIMIT :limit OFFSET :offset"
    
    result = db.execute(text(query), params)
    logs = result.fetchall()
    
    return [TrainingLogResponse(**dict(log)) for log in logs]

@router.delete("/training-jobs/{job_id}/cancel")
async def cancel_training_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Cancel a running training job
    """
    # Verify job belongs to user's bot
    result = db.execute(
        text("""
            SELECT tj.id, tj.status
            FROM training_jobs tj
            JOIN bots b ON tj.bot_id = b.id
            WHERE tj.id = :job_id AND b.user_id = :user_id
        """),
        {"job_id": job_id, "user_id": current_user.id}
    )
    
    job = result.fetchone()
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    if job.status not in ['pending', 'running']:
        raise HTTPException(
            status_code=400, 
            detail="Can only cancel pending or running jobs"
        )
    
    # Kill the process if it exists
    if job_id in active_training_jobs:
        process = active_training_jobs[job_id]
        process.terminate()
        del active_training_jobs[job_id]
    
    # Update job status
    db.execute(
        text("""
            UPDATE training_jobs 
            SET status = 'cancelled', completed_at = NOW() 
            WHERE id = :job_id
        """),
        {"job_id": job_id}
    )
    
    # Add cancellation log
    db.execute(
        text("""
            INSERT INTO training_logs (training_job_id, log_level, message) 
            VALUES (:job_id, 'WARNING', 'Training job cancelled by user')
        """),
        {"job_id": job_id}
    )
    
    db.commit()
    
    return {"message": "Training job cancelled successfully"}

@router.delete("/training-jobs/{job_id}/delete")
async def delete_training_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete a training job and all its logs
    """
    # Verify job belongs to user's bot
    result = db.execute(
        text("""
            SELECT tj.id, tj.status
            FROM training_jobs tj
            JOIN bots b ON tj.bot_id = b.id
            WHERE tj.id = :job_id AND b.user_id = :user_id
        """),
        {"job_id": job_id, "user_id": current_user.id}
    )
    
    job = result.fetchone()
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    # Cannot delete running jobs
    if job.status in ['pending', 'running']:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete a job that is still running. Cancel it first."
        )
    
    # Delete the job (logs will be deleted automatically due to CASCADE)
    db.execute(
        text("DELETE FROM training_jobs WHERE id = :job_id"),
        {"job_id": job_id}
    )
    
    db.commit()
    
    return {"message": "Training job and logs deleted successfully"}
