"""
Training data parsers for different file formats
"""
import json
import yaml
import csv
import re
from typing import List, Dict, Optional
from io import StringIO


class TrainingDataParser:
    """Parse training data from various formats"""
    
    @staticmethod
    def parse_json(content: str) -> List[Dict]:
        """
        Parse JSON format
        Expected: [{"user": "...", "bot": "...", "intent": "..."}]
        """
        try:
            data = json.loads(content)
            if not isinstance(data, list):
                raise ValueError("JSON must be an array")
            
            result = []
            for item in data:
                if "user" in item and "bot" in item:
                    result.append({
                        "user": item["user"],
                        "bot": item["bot"],
                        "intent": item.get("intent", "unknown")
                    })
            
            return result
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")
    
    @staticmethod
    def parse_yaml(content: str) -> List[Dict]:
        """
        Parse YAML format
        
        Format 1 - Rasa NLU:
        nlu:
        - intent: greeting
          examples: |
            - hi
            - hello
        
        Format 2 - Simple:
        - user: hi
          bot: Hello!
          intent: greeting
        """
        try:
            data = yaml.safe_load(content)
            
            # Check if Rasa NLU format
            if isinstance(data, dict) and "nlu" in data:
                return TrainingDataParser._parse_rasa_nlu(data)
            
            # Simple YAML list format
            elif isinstance(data, list):
                result = []
                for item in data:
                    if "user" in item and "bot" in item:
                        result.append({
                            "user": item["user"],
                            "bot": item["bot"],
                            "intent": item.get("intent", "unknown")
                        })
                return result
            
            else:
                raise ValueError("Unsupported YAML format")
                
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {str(e)}")
    
    @staticmethod
    def _parse_rasa_nlu(data: dict) -> List[Dict]:
        """Parse Rasa NLU YAML format"""
        result = []
        
        for item in data.get("nlu", []):
            if "intent" in item and "examples" in item:
                intent = item["intent"]
                examples = item["examples"]
                
                # Parse examples (format: "- example text")
                lines = examples.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('-'):
                        user_text = line[1:].strip()
                        # Remove entity annotations [text](entity)
                        user_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', user_text)
                        
                        result.append({
                            "user": user_text,
                            "bot": f"Response for {intent}",  # Placeholder
                            "intent": intent
                        })
        
        return result
    
    @staticmethod
    def parse_csv(content: str) -> List[Dict]:
        """
        Parse CSV format
        Expected columns: user, bot, intent (or variations)
        """
        try:
            csv_file = StringIO(content)
            reader = csv.DictReader(csv_file)
            
            result = []
            for row in reader:
                # Try different column names
                user_text = (row.get("user") or row.get("User") or 
                           row.get("question") or row.get("Question") or
                           row.get("user_message") or "").strip()
                
                bot_text = (row.get("bot") or row.get("Bot") or
                          row.get("answer") or row.get("Answer") or
                          row.get("bot_response") or "").strip()
                
                intent = (row.get("intent") or row.get("Intent") or
                         row.get("category") or row.get("Category") or
                         "unknown").strip()
                
                if user_text and bot_text:
                    result.append({
                        "user": user_text,
                        "bot": bot_text,
                        "intent": intent
                    })
            
            return result
            
        except Exception as e:
            raise ValueError(f"Invalid CSV: {str(e)}")
    
    @staticmethod
    def parse_txt(content: str) -> List[Dict]:
        """
        Parse plain text format
        
        Supported formats:
        1. User: question
           Bot: answer
           Intent: intent_name
        
        2. Q: question
           A: answer
           #intent_name
        
        3. question
           answer
           ---
        """
        result = []
        lines = content.strip().split('\n')
        
        current_item = {}
        
        for line in lines:
            line = line.strip()
            
            # Empty line = new item
            if not line or line == '---':
                if 'user' in current_item and 'bot' in current_item:
                    if 'intent' not in current_item:
                        current_item['intent'] = TrainingDataParser._auto_detect_intent(
                            current_item['user']
                        )
                    result.append(current_item)
                current_item = {}
                continue
            
            # Parse User/Q
            if line.lower().startswith('user:') or line.lower().startswith('q:'):
                current_item['user'] = re.sub(r'^(user:|q:)\s*', '', line, flags=re.IGNORECASE)
            
            # Parse Bot/A
            elif line.lower().startswith('bot:') or line.lower().startswith('a:'):
                current_item['bot'] = re.sub(r'^(bot:|a:)\s*', '', line, flags=re.IGNORECASE)
            
            # Parse Intent
            elif line.lower().startswith('intent:') or line.startswith('#'):
                current_item['intent'] = re.sub(r'^(intent:|#)\s*', '', line, flags=re.IGNORECASE)
            
            # Fallback: alternate lines
            elif 'user' not in current_item:
                current_item['user'] = line
            elif 'bot' not in current_item:
                current_item['bot'] = line
        
        # Add last item
        if 'user' in current_item and 'bot' in current_item:
            if 'intent' not in current_item:
                current_item['intent'] = TrainingDataParser._auto_detect_intent(
                    current_item['user']
                )
            result.append(current_item)
        
        return result
    
    @staticmethod
    def _auto_detect_intent(text: str) -> str:
        """Auto-detect intent from user message"""
        text_lower = text.lower()
        
        # Greeting
        if re.search(r'^(xin )?chào|^hi$|^hello', text_lower):
            return 'chao_hoi'
        
        # Pricing
        if re.search(r'giá|bao nhiêu|tiền|chi phí', text_lower):
            return 'hoi_gia'
        
        # Contact
        if re.search(r'liên hệ|số điện thoại|email|địa chỉ', text_lower):
            return 'lien_he'
        
        # Features
        if re.search(r'tính năng|chức năng|làm gì', text_lower):
            return 'tinh_nang'
        
        # Thanks
        if re.search(r'cảm ơn|thanks', text_lower):
            return 'cam_on'
        
        # Goodbye
        if re.search(r'tạm biệt|bye', text_lower):
            return 'tam_biet'
        
        return 'unknown'
    
    @staticmethod
    def parse_markdown(content: str) -> List[Dict]:
        """
        Parse Markdown format (Rasa 2.x style)
        
        ## intent:greeting
        - hi
        - hello
        - hey
        """
        result = []
        current_intent = None
        
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Intent header
            if line.startswith('##'):
                match = re.search(r'##\s*intent:(\w+)', line)
                if match:
                    current_intent = match.group(1)
            
            # Example
            elif line.startswith('-') and current_intent:
                user_text = line[1:].strip()
                # Remove entity annotations
                user_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', user_text)
                
                result.append({
                    "user": user_text,
                    "bot": f"Response for {current_intent}",
                    "intent": current_intent
                })
        
        return result
    
    @staticmethod
    def detect_format(filename: str, content: str) -> str:
        """Auto-detect file format"""
        extension = filename.lower().split('.')[-1]
        
        if extension == 'json':
            return 'json'
        elif extension in ['yml', 'yaml']:
            return 'yaml'
        elif extension == 'csv':
            return 'csv'
        elif extension in ['txt', 'text']:
            return 'txt'
        elif extension in ['md', 'markdown']:
            return 'markdown'
        
        # Try to detect from content
        content_sample = content[:200].strip()
        
        if content_sample.startswith('[') or content_sample.startswith('{'):
            return 'json'
        elif content_sample.startswith('nlu:') or 'intent:' in content_sample:
            return 'yaml'
        elif '##' in content_sample and 'intent:' in content_sample:
            return 'markdown'
        elif ',' in content_sample and '\n' in content_sample:
            return 'csv'
        
        return 'txt'
    
    @staticmethod
    def parse(filename: str, content: str, format_hint: str = None) -> List[Dict]:
        """
        Parse training data from any supported format
        
        Args:
            filename: Original filename
            content: File content as string
            format_hint: Optional format override
        
        Returns:
            List of training data dicts
        """
        format_type = format_hint or TrainingDataParser.detect_format(filename, content)
        
        parsers = {
            'json': TrainingDataParser.parse_json,
            'yaml': TrainingDataParser.parse_yaml,
            'yml': TrainingDataParser.parse_yaml,
            'csv': TrainingDataParser.parse_csv,
            'txt': TrainingDataParser.parse_txt,
            'text': TrainingDataParser.parse_txt,
            'markdown': TrainingDataParser.parse_markdown,
            'md': TrainingDataParser.parse_markdown
        }
        
        parser = parsers.get(format_type)
        if not parser:
            raise ValueError(f"Unsupported format: {format_type}")
        
        return parser(content)
    
    @staticmethod
    def enhance_with_intelligent_classification(
        data: List[Dict],
        bot_id: int,
        rasa_url: str = "http://rasa:5005"
    ) -> List[Dict]:
        """
        Enhance training data with intelligent intent classification using Rasa
        
        Args:
            data: Parsed training data (may have 'unknown' intents)
            bot_id: Bot ID to use its trained model
            rasa_url: Rasa server URL
            
        Returns:
            Enhanced training data with classified intents
        """
        from .intent_classifier import HybridIntentClassifier
        
        classifier = HybridIntentClassifier(rasa_url)
        classifier.initialize(bot_id)
        
        enhanced_data = []
        for item in data:
            # Only classify if intent is unknown or missing
            if item.get('intent') in [None, '', 'unknown']:
                detected_intent = classifier.classify(item['user'])
                item['intent'] = detected_intent
            
            enhanced_data.append(item)
        
        return enhanced_data
