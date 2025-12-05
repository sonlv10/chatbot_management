"""
Rasa interaction service - Chat with trained models
"""
import os
import sys
import requests
from typing import Dict, List, Optional

# Fix encoding issues on Windows when handling Vietnamese text
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class RasaService:
    """Service to interact with Rasa server"""
    
    def __init__(self, rasa_url: str = os.getenv("RASA_SERVER_URL", "http://localhost:5005")):
        self.rasa_url = rasa_url.rstrip('/')
        # Track currently loaded model to avoid reloading
        self._loaded_model_path = None
    
    def chat(self, bot_id: int, message: str, sender_id: str = "user") -> Dict:
        """
        Send message to Rasa bot and get response with intent classification
        
        Args:
            bot_id: Bot ID (model loaded in Rasa)
            message: User message
            sender_id: Sender identifier for session tracking
        
        Returns:
            Dict with response data including intent and confidence
        """
        # Use bot-specific sender to maintain separate conversation contexts
        bot_sender_id = f"bot_{bot_id}_{sender_id}"
        
        # Get bot response via webhook (includes intent in response)
        webhook_endpoint = f"{self.rasa_url}/webhooks/rest/webhook"
        webhook_payload = {
            "sender": bot_sender_id,
            "message": message
        }
        
        intent = None
        confidence = None
        entities = []
        
        try:
            response = requests.post(webhook_endpoint, json=webhook_payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Try to get intent from tracker (fast, non-blocking)
            try:
                tracker_endpoint = f"{self.rasa_url}/conversations/{bot_sender_id}/tracker"
                tracker_response = requests.get(tracker_endpoint, timeout=2)
                if tracker_response.status_code == 200:
                    tracker_data = tracker_response.json()
                    latest_event = tracker_data.get('latest_message', {})
                    intent_data = latest_event.get('intent', {})
                    intent = intent_data.get('name')
                    confidence = intent_data.get('confidence')
                    entities = latest_event.get('entities', [])
            except Exception as e:
                # Safely print error message
                try:
                    print(f"[DEBUG] Could not get intent from tracker: {repr(e)}")
                except:
                    pass
            
            # Parse response
            if data and len(data) > 0:
                # Rasa may return multiple messages - combine them
                bot_responses = [msg.get('text', '') for msg in data if 'text' in msg]
                bot_response = '\n'.join(bot_responses) if bot_responses else ''
                
                return {
                    "status": "success",
                    "message": bot_response,
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "raw_response": data
                }
            else:
                return {
                    "status": "no_response",
                    "message": "Bot không trả lời",
                    "intent": intent,
                    "confidence": confidence,
                    "raw_response": data
                }
        
        except requests.RequestException as e:
            # Safely encode error message to handle Vietnamese characters
            error_msg = repr(e) if isinstance(e, Exception) else str(e)
            return {
                "status": "error",
                "error_message": f"Failed to connect to Rasa: {error_msg}",
                "intent": intent,
                "confidence": confidence
            }
        except Exception as e:
            # Safely encode error message to handle Vietnamese characters
            error_msg = repr(e) if hasattr(e, '__repr__') else "Unknown error"
            return {
                "status": "error",
                "error_message": error_msg,
                "intent": intent,
                "confidence": confidence
            }
    
    def load_model(self, bot_id: int, model_path: str) -> Dict:
        """
        Load a specific model in Rasa server using HTTP API
        
        Args:
            bot_id: Bot ID
            model_path: Path to model file (absolute path from database)
        
        Returns:
            Dict with status
        """
        endpoint = f"{self.rasa_url}/model"
        
        # Model path is stored as: C:\chatbot_management\rasa\models\bot_X\modelfile.tar.gz
        # If Rasa runs from project root: use rasa/models/bot_X/modelfile.tar.gz
        # If Rasa runs from rasa/ directory: use models/bot_X/modelfile.tar.gz
        
        print(f"[DEBUG] Original model_path: {model_path}")
        
        # Get project root (backend's parent directory)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        rasa_dir = os.path.join(project_root, "rasa")
        print(f"[DEBUG] Project root: {project_root}")
        print(f"[DEBUG] Rasa directory: {rasa_dir}")
        
        # Convert to absolute path first
        if os.path.isabs(model_path):
            abs_model_path = os.path.abspath(model_path)
        else:
            abs_model_path = os.path.abspath(os.path.join(project_root, model_path))
        
        print(f"[DEBUG] Absolute model path: {abs_model_path}")
        
        # Determine if path is inside rasa directory
        # If yes, make path relative to rasa directory (for when Rasa runs from rasa/)
        try:
            if abs_model_path.startswith(rasa_dir):
                # Path is inside rasa/, make it relative to rasa/
                rasa_model_path = os.path.relpath(abs_model_path, rasa_dir).replace("\\", "/")
                print(f"[DEBUG] Path relative to rasa/: {rasa_model_path}")
            else:
                # Path outside rasa/, make it relative to project root
                rasa_model_path = os.path.relpath(abs_model_path, project_root).replace("\\", "/")
                print(f"[DEBUG] Path relative to project: {rasa_model_path}")
        except ValueError:
            # If on different drives, use absolute path
            rasa_model_path = abs_model_path.replace("\\", "/")
        
        print(f"[DEBUG] Final rasa_model_path: {rasa_model_path}")
        
        # Check if this model is already loaded in memory cache
        if self._loaded_model_path == rasa_model_path:
            print(f"[DEBUG] Model {rasa_model_path} already loaded (cached), skipping")
            return {
                "status": "success",
                "message": f"Model already loaded for bot {bot_id}",
                "model_path": rasa_model_path
            }
        
        # Check if model is already loaded in Rasa server
        try:
            status_response = requests.get(f"{self.rasa_url}/status", timeout=5)
            if status_response.status_code == 200:
                status_data = status_response.json()
                loaded_model = status_data.get('model_file', '')
                # Extract just the filename from our path
                our_model_file = os.path.basename(rasa_model_path)
                if loaded_model == our_model_file:
                    print(f"[DEBUG] Model {our_model_file} already loaded in Rasa server, updating cache")
                    self._loaded_model_path = rasa_model_path
                    return {
                        "status": "success",
                        "message": f"Model already loaded for bot {bot_id}",
                        "model_path": rasa_model_path
                    }
        except Exception as e:
            # Safely print error message
            try:
                print(f"[WARN] Could not check Rasa status: {repr(e)}")
            except:
                pass
        
        # Rasa expects the model path
        payload = {
            "model_file": rasa_model_path
        }
        
        try:
            print(f"[DEBUG] Loading NEW model: {rasa_model_path}")
            # PUT request to load new model (may take long time for first load)
            response = requests.put(
                endpoint,
                json=payload,
                timeout=120  # Increased to 120s for slow model loading
            )
            
            if response.status_code == 204:
                # Remember loaded model
                self._loaded_model_path = rasa_model_path
                return {
                    "status": "success",
                    "message": f"Model loaded successfully for bot {bot_id}",
                    "model_path": rasa_model_path
                }
            else:
                return {
                    "status": "error",
                    "error_message": f"Failed to load model: {response.text}",
                    "status_code": response.status_code
                }
        
        except requests.RequestException as e:
            return {
                "status": "error",
                "error_message": f"Failed to connect to Rasa: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    def get_model_status(self, bot_id: int) -> Dict:
        """Get status of loaded model"""
        endpoint = f"{self.rasa_url}/status"
        
        try:
            response = requests.get(endpoint, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "status": "success",
                "data": data
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e)
            }
