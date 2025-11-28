"""
Rasa interaction service - Chat with trained models
"""
import os
import requests
from typing import Dict, List, Optional


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
        
        # First, parse message to get intent classification
        parse_endpoint = f"{self.rasa_url}/model/parse"
        parse_payload = {
            "text": message,
            "message_id": f"{bot_sender_id}_{message[:20]}"
        }
        
        intent = None
        confidence = None
        entities = []
        
        try:
            parse_response = requests.post(parse_endpoint, json=parse_payload, timeout=5)
            if parse_response.status_code == 200:
                parse_data = parse_response.json()
                intent_data = parse_data.get('intent', {})
                intent = intent_data.get('name')
                confidence = intent_data.get('confidence')
                entities = parse_data.get('entities', [])
        except Exception as e:
            print(f"[WARN] Failed to parse intent: {str(e)}")
        
        # Then get bot response via webhook
        webhook_endpoint = f"{self.rasa_url}/webhooks/rest/webhook"
        webhook_payload = {
            "sender": bot_sender_id,
            "message": message
        }
        
        try:
            response = requests.post(webhook_endpoint, json=webhook_payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
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
            return {
                "status": "error",
                "error_message": f"Failed to connect to Rasa: {str(e)}",
                "intent": intent,
                "confidence": confidence
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e),
                "intent": intent,
                "confidence": confidence
            }
    
    def load_model(self, bot_id: int, model_path: str) -> Dict:
        """
        Load a specific model in Rasa server using HTTP API
        
        Args:
            bot_id: Bot ID
            model_path: Path to model file (absolute path in container)
        
        Returns:
            Dict with status
        """
        endpoint = f"{self.rasa_url}/model"
        
        # Convert backend path to Rasa path
        # Backend: /app/models/bot_X/models/bot_X.tar.gz
        # Rasa:    /models/bot_X/models/bot_X.tar.gz
        rasa_model_path = model_path.replace('/app/models', '/models')
        
        # Check if this model is already loaded
        if self._loaded_model_path == rasa_model_path:
            print(f"[DEBUG] Model {rasa_model_path} already loaded, skipping")
            return {
                "status": "success",
                "message": f"Model already loaded for bot {bot_id}",
                "model_path": rasa_model_path
            }
        
        # Rasa expects the model path
        payload = {
            "model_file": rasa_model_path
        }
        
        try:
            print(f"[DEBUG] Loading NEW model: {rasa_model_path}")
            # PUT request to load new model
            response = requests.put(
                endpoint,
                json=payload,
                timeout=30
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
