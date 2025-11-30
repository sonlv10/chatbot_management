"""
Custom actions for Rasa chatbot to handle conversation context
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionRememberContext(Action):
    """Remember context from the conversation"""
    
    def name(self) -> Text:
        return "action_remember_context"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the last intent
        last_intent = tracker.latest_message.get('intent', {}).get('name')
        
        # Get entities from the message
        entities = tracker.latest_message.get('entities', [])
        
        events = []
        
        # Store previous intent
        if last_intent:
            events.append(SlotSet("previous_intent", last_intent))
        
        # Store entities in appropriate slots
        for entity in entities:
            entity_type = entity.get('entity')
            entity_value = entity.get('value')
            
            if entity_type in ['user_name', 'product_name', 'location', 'phone_number', 'email']:
                events.append(SlotSet(entity_type, entity_value))
        
        # Store all context info
        context_info = {
            'last_intent': last_intent,
            'entities': entities,
            'message': tracker.latest_message.get('text')
        }
        events.append(SlotSet("context_info", context_info))
        
        return events


class ActionUseContext(Action):
    """Use stored context to provide personalized responses"""
    
    def name(self) -> Text:
        return "action_use_context"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get stored information from slots
        user_name = tracker.get_slot("user_name")
        product_name = tracker.get_slot("product_name")
        location = tracker.get_slot("location")
        previous_intent = tracker.get_slot("previous_intent")
        
        # Build contextualized response
        response = "Dựa trên thông tin trước đó"
        
        if user_name:
            response += f", anh/chị {user_name}"
        
        if product_name:
            response += f" đang quan tâm đến {product_name}"
        
        if location:
            response += f" tại {location}"
        
        response += ". Tôi có thể giúp gì thêm cho anh/chị?"
        
        dispatcher.utter_message(text=response)
        
        return []


class ActionDefaultFallback(Action):
    """Fallback action when confidence is low"""
    
    def name(self) -> Text:
        return "action_default_fallback"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get context to provide better fallback
        previous_intent = tracker.get_slot("previous_intent")
        
        message = "Xin lỗi, tôi chưa hiểu rõ ý của bạn."
        
        if previous_intent:
            message += f" Trước đó chúng ta đang nói về {previous_intent}. Bạn có thể nói rõ hơn được không?"
        else:
            message += " Bạn có thể diễn đạt lại câu hỏi được không?"
        
        dispatcher.utter_message(text=message)
        
        return []
