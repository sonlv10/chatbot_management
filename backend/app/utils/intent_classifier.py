"""
Intelligent intent classification using Rasa NLU
"""
import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Use Rasa NLU to classify intents intelligently"""
    
    def __init__(self, rasa_url: str = "http://rasa:5005"):
        self.rasa_url = rasa_url
    
    def classify_batch(
        self, 
        messages: List[str], 
        model_name: str,
        confidence_threshold: float = 0.6
    ) -> List[str]:
        """
        Classify multiple messages using trained Rasa model
        
        Args:
            messages: List of user messages to classify
            model_name: Name of trained model to use
            confidence_threshold: Minimum confidence (0-1) to accept classification
            
        Returns:
            List of detected intents
        """
        results = []
        
        for message in messages:
            intent = self.classify_single(message, model_name, confidence_threshold)
            results.append(intent)
        
        return results
    
    def classify_single(
        self, 
        message: str, 
        model_name: str,
        confidence_threshold: float = 0.6
    ) -> str:
        """
        Classify a single message
        
        Returns:
            Detected intent or 'unknown' if confidence too low
        """
        try:
            # Parse message using Rasa NLU
            response = requests.post(
                f"{self.rasa_url}/model/parse",
                json={
                    "text": message,
                    "message_id": f"classify_{hash(message)}"
                },
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                intent_data = data.get("intent", {})
                intent_name = intent_data.get("name", "unknown")
                confidence = intent_data.get("confidence", 0.0)
                
                # Only return intent if confidence is high enough
                if confidence >= confidence_threshold:
                    logger.info(f"Classified '{message}' as '{intent_name}' (confidence: {confidence:.2f})")
                    return intent_name
                else:
                    logger.warning(f"Low confidence {confidence:.2f} for '{message}', using 'unknown'")
                    return "unknown"
            else:
                logger.error(f"Rasa parse failed: {response.status_code}")
                return "unknown"
                
        except requests.RequestException as e:
            logger.error(f"Error calling Rasa: {str(e)}")
            return "unknown"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return "unknown"
    
    def get_available_intents(self, model_name: str) -> List[str]:
        """
        Get list of intents from trained model
        
        Returns:
            List of intent names
        """
        try:
            # Get model metadata
            response = requests.get(
                f"{self.rasa_url}/model/metadata",
                timeout=5
            )
            
            if response.status_code == 200:
                metadata = response.json()
                # Extract intents from domain
                intents = []
                if "domain" in metadata:
                    domain = metadata["domain"]
                    if "intents" in domain:
                        intents = domain["intents"]
                
                return intents
            
        except Exception as e:
            logger.error(f"Error getting intents: {str(e)}")
        
        return []
    
    def is_rasa_available(self) -> bool:
        """Check if Rasa server is running"""
        try:
            response = requests.get(f"{self.rasa_url}/status", timeout=2)
            return response.status_code == 200
        except:
            return False


class HybridIntentClassifier:
    """
    Hybrid classifier: use Rasa if available, fallback to regex
    """
    
    def __init__(self, rasa_url: str = "http://rasa:5005"):
        self.rasa_classifier = IntentClassifier(rasa_url)
        self.use_rasa = False
    
    def initialize(self, bot_id: int) -> bool:
        """
        Initialize classifier for a specific bot
        
        Args:
            bot_id: Bot ID to use its trained model
            
        Returns:
            True if Rasa is available and will be used
        """
        # Check if Rasa is available
        if not self.rasa_classifier.is_rasa_available():
            logger.warning("Rasa not available, will use regex fallback")
            self.use_rasa = False
            return False
        
        # Check if bot has trained model
        model_name = f"bot_{bot_id}"
        try:
            response = requests.get(
                f"{self.rasa_classifier.rasa_url}/status",
                timeout=2
            )
            if response.status_code == 200:
                self.model_name = model_name
                self.use_rasa = True
                logger.info(f"Using Rasa NLU for intent classification (model: {model_name})")
                return True
        except:
            pass
        
        logger.warning("Bot model not found, will use regex fallback")
        self.use_rasa = False
        return False
    
    def classify(self, message: str) -> str:
        """
        Classify message using best available method
        
        Args:
            message: User message
            
        Returns:
            Detected intent
        """
        if self.use_rasa:
            return self.rasa_classifier.classify_single(
                message, 
                self.model_name,
                confidence_threshold=0.5  # Lower threshold for auto-classification
            )
        else:
            return self._regex_classify(message)
    
    def _regex_classify(self, text: str) -> str:
        """Fallback regex-based classification"""
        import re
        
        text_lower = text.lower()
        
        # Greeting
        if re.search(r'^(xin )?chào|^hi$|^hello|^hey', text_lower):
            return 'chao_hoi'
        
        # Pricing
        if re.search(r'giá|bao nhiêu|tiền|chi phí|phí', text_lower):
            return 'hoi_gia'
        
        # Contact
        if re.search(r'liên hệ|số điện thoại|email|địa chỉ|hotline', text_lower):
            return 'lien_he'
        
        # Features
        if re.search(r'tính năng|chức năng|làm gì|hỗ trợ gì|có gì', text_lower):
            return 'tinh_nang'
        
        # Shipping
        if re.search(r'giao hàng|vận chuyển|ship|giao tận nơi', text_lower):
            return 'giao_hang'
        
        # Payment
        if re.search(r'thanh toán|trả tiền|payment|cod', text_lower):
            return 'thanh_toan'
        
        # Warranty
        if re.search(r'bảo hành|warranty|đổi trả', text_lower):
            return 'bao_hanh'
        
        # Thanks
        if re.search(r'cảm ơn|thanks|thank you', text_lower):
            return 'cam_on'
        
        # Goodbye
        if re.search(r'tạm biệt|bye|goodbye', text_lower):
            return 'tam_biet'
        
        # Order status
        if re.search(r'đơn hàng|order|kiểm tra đơn', text_lower):
            return 'don_hang'
        
        return 'unknown'
