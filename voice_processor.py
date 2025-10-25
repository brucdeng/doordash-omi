"""
Voice Command Processor
Handles voice command detection, intent extraction, and menu item matching
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional
import openai

logger = logging.getLogger(__name__)

class VoiceProcessor:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Voice command triggers
        self.order_triggers = [
            "order", "get", "buy", "want", "need", "craving", "hungry",
            "pizza", "food", "delivery", "eat", "lunch", "dinner"
        ]
        
        # Food item keywords
        self.food_keywords = [
            "pizza", "burger", "pasta", "salad", "sandwich", "sushi",
            "chinese", "mexican", "italian", "thai", "indian", "japanese"
        ]
        
        # Location keywords
        self.location_keywords = [
            "closest", "nearby", "near me", "close", "local", "around here"
        ]
    
    def is_food_order_command(self, segments: List[str]) -> bool:
        """
        Check if the voice command is about ordering food
        """
        full_text = " ".join(segments).lower()
        
        # Check for order triggers
        has_order_trigger = any(trigger in full_text for trigger in self.order_triggers)
        
        # Check for food keywords
        has_food_keyword = any(food in full_text for food in self.food_keywords)
        
        return has_order_trigger or has_food_keyword
    
    def extract_order_intent(self, segments: List[str]) -> Optional[Dict[str, Any]]:
        """
        Extract order intent from voice segments using AI
        """
        try:
            full_text = " ".join(segments)
            
            if self.openai_api_key:
                return self._extract_intent_with_ai(full_text)
            else:
                return self._extract_intent_simple(full_text)
                
        except Exception as e:
            logger.error(f"Error extracting order intent: {str(e)}")
            return None
    
    def _extract_intent_with_ai(self, text: str) -> Dict[str, Any]:
        """
        Use OpenAI to extract order intent
        """
        try:
            prompt = f"""
            Extract order information from this voice command: "{text}"
            
            Return a JSON object with:
            - food_item: the main food item requested
            - location_preference: "closest" or "nearby" if mentioned
            - dietary_restrictions: any mentioned dietary needs
            - quantity: number of items (default 1)
            - special_requests: any special instructions
            
            Example: {{"food_item": "pepperoni pizza", "location_preference": "closest", "dietary_restrictions": [], "quantity": 1, "special_requests": ""}}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"AI intent extraction failed: {str(e)}")
            return self._extract_intent_simple(text)
    
    def _extract_intent_simple(self, text: str) -> Dict[str, Any]:
        """
        Simple rule-based intent extraction
        """
        text_lower = text.lower()
        
        # Extract food item
        food_item = self._extract_food_item(text_lower)
        
        # Check for location preference
        location_preference = "closest" if any(loc in text_lower for loc in self.location_keywords) else ""
        
        # Extract dietary restrictions
        dietary_restrictions = self._extract_dietary_restrictions(text_lower)
        
        # Extract quantity
        quantity = self._extract_quantity(text_lower)
        
        return {
            "food_item": food_item,
            "location_preference": location_preference,
            "dietary_restrictions": dietary_restrictions,
            "quantity": quantity,
            "special_requests": ""
        }
    
    def _extract_food_item(self, text: str) -> str:
        """Extract the main food item from text"""
        # Look for common food patterns
        food_patterns = [
            r"(pepperoni|margherita|cheese)\s+pizza",
            r"pizza\s+(pepperoni|margherita|cheese)",
            r"(chicken|beef|veggie)\s+burger",
            r"burger\s+(chicken|beef|veggie)",
            r"(caesar|garden|chicken)\s+salad",
            r"salad\s+(caesar|garden|chicken)"
        ]
        
        for pattern in food_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        # Fallback to first food keyword found
        for food in self.food_keywords:
            if food in text:
                return food
        
        return "pizza"  # Default fallback
    
    def _extract_dietary_restrictions(self, text: str) -> List[str]:
        """Extract dietary restrictions from text"""
        restrictions = []
        
        dietary_keywords = {
            "vegetarian": ["vegetarian", "veggie", "no meat"],
            "vegan": ["vegan", "no dairy", "plant-based"],
            "gluten-free": ["gluten-free", "no gluten", "gf"],
            "dairy-free": ["dairy-free", "no dairy", "lactose-free"],
            "keto": ["keto", "low carb", "ketogenic"],
            "halal": ["halal", "halal food"],
            "kosher": ["kosher", "kosher food"]
        }
        
        for restriction, keywords in dietary_keywords.items():
            if any(keyword in text for keyword in keywords):
                restrictions.append(restriction)
        
        return restrictions
    
    def _extract_quantity(self, text: str) -> int:
        """Extract quantity from text"""
        # Look for numbers
        numbers = re.findall(r'\b(\d+)\b', text)
        if numbers:
            return int(numbers[0])
        
        # Look for word numbers
        word_numbers = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "a": 1, "an": 1, "single": 1, "double": 2
        }
        
        for word, num in word_numbers.items():
            if word in text:
                return num
        
        return 1  # Default quantity
    
    def find_matching_menu_items(self, order_intent: Dict[str, Any], menu_items: List[Dict]) -> List[Dict]:
        """
        Find menu items that match the order intent
        """
        try:
            food_item = order_intent.get("food_item", "").lower()
            dietary_restrictions = order_intent.get("dietary_restrictions", [])
            quantity = order_intent.get("quantity", 1)
            
            matching_items = []
            
            for item in menu_items:
                if not item.get("is_available", True):
                    continue
                
                # Check if item matches the food request
                if self._item_matches_food_request(item, food_item):
                    # Check dietary restrictions
                    if self._item_satisfies_dietary_restrictions(item, dietary_restrictions):
                        # Add quantity to item
                        item_copy = item.copy()
                        item_copy["quantity"] = quantity
                        matching_items.append(item_copy)
            
            # Sort by relevance (exact match first, then partial match)
            matching_items.sort(key=lambda x: self._calculate_relevance_score(x, food_item), reverse=True)
            
            return matching_items[:3]  # Return top 3 matches
            
        except Exception as e:
            logger.error(f"Error finding matching menu items: {str(e)}")
            return []
    
    def _item_matches_food_request(self, item: Dict, food_request: str) -> bool:
        """Check if menu item matches the food request"""
        item_name = item.get("name", "").lower()
        item_description = item.get("description", "").lower()
        
        # Exact match
        if food_request in item_name or food_request in item_description:
            return True
        
        # Partial match for key terms
        food_terms = food_request.split()
        for term in food_terms:
            if term in item_name or term in item_description:
                return True
        
        return False
    
    def _item_satisfies_dietary_restrictions(self, item: Dict, restrictions: List[str]) -> bool:
        """Check if item satisfies dietary restrictions"""
        if not restrictions:
            return True
        
        item_dietary = item.get("dietary_info", [])
        
        for restriction in restrictions:
            if restriction == "vegetarian":
                if "contains-meat" in item_dietary:
                    return False
            elif restriction == "vegan":
                if "contains-dairy" in item_dietary or "contains-meat" in item_dietary:
                    return False
            elif restriction == "gluten-free":
                if "contains-gluten" in item_dietary:
                    return False
            elif restriction == "dairy-free":
                if "contains-dairy" in item_dietary:
                    return False
        
        return True
    
    def _calculate_relevance_score(self, item: Dict, food_request: str) -> int:
        """Calculate relevance score for menu item"""
        score = 0
        item_name = item.get("name", "").lower()
        item_description = item.get("description", "").lower()
        
        # Exact match in name gets highest score
        if food_request in item_name:
            score += 10
        
        # Partial match in name
        for word in food_request.split():
            if word in item_name:
                score += 5
        
        # Match in description
        if food_request in item_description:
            score += 3
        
        # Partial match in description
        for word in food_request.split():
            if word in item_description:
                score += 1
        
        return score
    
    def generate_order_summary(self, order_intent: Dict, restaurant: Dict, items: List[Dict]) -> str:
        """
        Generate a spoken summary of the order for confirmation
        """
        try:
            restaurant_name = restaurant.get("name", "Unknown Restaurant")
            total_price = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
            
            summary_parts = [
                f"I found {restaurant_name}",
                f"with {len(items)} item(s) for ${total_price:.2f}",
                f"Estimated delivery: {restaurant.get('delivery_time', '25-35 min')}"
            ]
            
            if items:
                item_names = [item.get("name", "Unknown Item") for item in items]
                summary_parts.append(f"Items: {', '.join(item_names)}")
            
            return ". ".join(summary_parts) + ". Would you like me to place this order?"
            
        except Exception as e:
            logger.error(f"Error generating order summary: {str(e)}")
            return "I found a restaurant and items for your order. Would you like me to place it?"
