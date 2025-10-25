"""
User Preferences Manager
Handles user preferences, delivery addresses, dietary restrictions, and order history
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import os

logger = logging.getLogger(__name__)

class UserPreferences:
    def __init__(self):
        self.storage_file = "user_preferences.json"
        self.preferences = {}
        self.order_history = {}
        self._load_preferences()
    
    def _load_preferences(self):
        """Load user preferences from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.preferences = data.get("preferences", {})
                    self.order_history = data.get("order_history", {})
        except Exception as e:
            logger.error(f"Error loading user preferences: {str(e)}")
            self.preferences = {}
            self.order_history = {}
    
    def _save_preferences(self):
        """Save user preferences to storage file"""
        try:
            data = {
                "preferences": self.preferences,
                "order_history": self.order_history,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving user preferences: {str(e)}")
    
    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        return self.preferences.get(user_id, {
            "delivery_address": "",
            "dietary_restrictions": [],
            "favorite_restaurants": [],
            "payment_method": "",
            "delivery_instructions": "",
            "notification_preferences": {
                "order_updates": True,
                "promotions": True
            }
        })
    
    def update_preferences(self, user_id: str, new_preferences: Dict[str, Any]):
        """Update user preferences"""
        try:
            if user_id not in self.preferences:
                self.preferences[user_id] = {}
            
            self.preferences[user_id].update(new_preferences)
            self.preferences[user_id]["last_updated"] = datetime.now().isoformat()
            self._save_preferences()
            logger.info(f"Updated preferences for user {user_id}")
        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")
    
    def get_delivery_address(self, user_id: str) -> Optional[str]:
        """Get user's delivery address"""
        return self.preferences.get(user_id, {}).get("delivery_address")
    
    def set_delivery_address(self, user_id: str, address: str):
        """Set user's delivery address"""
        self.update_preferences(user_id, {"delivery_address": address})
    
    def get_dietary_restrictions(self, user_id: str) -> List[str]:
        """Get user's dietary restrictions"""
        return self.preferences.get(user_id, {}).get("dietary_restrictions", [])
    
    def set_dietary_restrictions(self, user_id: str, restrictions: List[str]):
        """Set user's dietary restrictions"""
        self.update_preferences(user_id, {"dietary_restrictions": restrictions})
    
    def get_favorite_restaurants(self, user_id: str) -> List[str]:
        """Get user's favorite restaurants"""
        return self.preferences.get(user_id, {}).get("favorite_restaurants", [])
    
    def add_favorite_restaurant(self, user_id: str, restaurant_id: str):
        """Add restaurant to user's favorites"""
        favorites = self.get_favorite_restaurants(user_id)
        if restaurant_id not in favorites:
            favorites.append(restaurant_id)
            self.update_preferences(user_id, {"favorite_restaurants": favorites})
    
    def get_preferred_restaurant(self, restaurants: List[Dict], user_id: str) -> Dict[str, Any]:
        """Get user's preferred restaurant from a list"""
        try:
            user_favorites = self.get_favorite_restaurants(user_id)
            dietary_restrictions = self.get_dietary_restrictions(user_id)
            
            # First, try to find a favorite restaurant
            for restaurant in restaurants:
                if restaurant.get("id") in user_favorites:
                    return restaurant
            
            # Filter by dietary restrictions
            suitable_restaurants = []
            for restaurant in restaurants:
                if self._restaurant_satisfies_dietary_restrictions(restaurant, dietary_restrictions):
                    suitable_restaurants.append(restaurant)
            
            if suitable_restaurants:
                # Return highest rated suitable restaurant
                return max(suitable_restaurants, key=lambda x: x.get("rating", 0))
            
            # Fallback to highest rated restaurant
            return max(restaurants, key=lambda x: x.get("rating", 0))
            
        except Exception as e:
            logger.error(f"Error getting preferred restaurant: {str(e)}")
            return restaurants[0] if restaurants else {}
    
    def _restaurant_satisfies_dietary_restrictions(self, restaurant: Dict, restrictions: List[str]) -> bool:
        """Check if restaurant satisfies dietary restrictions"""
        if not restrictions:
            return True
        
        # This is a simplified check - in reality, you'd need restaurant dietary info
        cuisine_type = restaurant.get("cuisine_type", "").lower()
        
        for restriction in restrictions:
            if restriction == "vegetarian":
                if cuisine_type in ["steakhouse", "bbq", "seafood"]:
                    return False
            elif restriction == "vegan":
                if cuisine_type in ["steakhouse", "bbq", "seafood", "italian"]:
                    return False
            elif restriction == "halal":
                if cuisine_type in ["pork", "bacon"]:
                    return False
        
        return True
    
    def get_order_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's order history"""
        return self.order_history.get(user_id, [])
    
    def update_order_history(self, user_id: str, order_data: Dict[str, Any]):
        """Update user's order history"""
        try:
            if user_id not in self.order_history:
                self.order_history[user_id] = []
            
            # Add order to history
            order_record = {
                "order_id": order_data.get("order_id"),
                "restaurant": order_data.get("restaurant", {}),
                "items": order_data.get("items", []),
                "total_price": order_data.get("total_price", 0),
                "order_date": datetime.now().isoformat(),
                "status": "completed"
            }
            
            self.order_history[user_id].append(order_record)
            
            # Keep only last 50 orders
            if len(self.order_history[user_id]) > 50:
                self.order_history[user_id] = self.order_history[user_id][-50:]
            
            self._save_preferences()
            logger.info(f"Updated order history for user {user_id}")
        except Exception as e:
            logger.error(f"Error updating order history: {str(e)}")
    
    def get_frequent_orders(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get user's most frequent orders for quick re-ordering"""
        try:
            order_history = self.get_order_history(user_id)
            
            # Count item frequencies
            item_counts = {}
            for order in order_history:
                for item in order.get("items", []):
                    item_name = item.get("name", "")
                    if item_name:
                        item_counts[item_name] = item_counts.get(item_name, 0) + 1
            
            # Sort by frequency
            frequent_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
            
            return [{"item_name": item, "frequency": count} for item, count in frequent_items[:limit]]
        except Exception as e:
            logger.error(f"Error getting frequent orders: {str(e)}")
            return []
    
    def get_usual_order(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's usual order (most recent order)"""
        try:
            order_history = self.get_order_history(user_id)
            if order_history:
                return order_history[-1]  # Most recent order
            return None
        except Exception as e:
            logger.error(f"Error getting usual order: {str(e)}")
            return None
    
    def get_restaurant_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user's restaurant preferences"""
        preferences = self.get_preferences(user_id)
        return {
            "favorite_restaurants": preferences.get("favorite_restaurants", []),
            "preferred_cuisine": preferences.get("preferred_cuisine", ""),
            "max_delivery_time": preferences.get("max_delivery_time", 45),
            "max_delivery_fee": preferences.get("max_delivery_fee", 5.00)
        }
    
    def set_restaurant_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Set user's restaurant preferences"""
        self.update_preferences(user_id, preferences)
    
    def get_payment_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user's payment preferences"""
        preferences = self.get_preferences(user_id)
        return {
            "payment_method": preferences.get("payment_method", ""),
            "tip_percentage": preferences.get("tip_percentage", 15),
            "auto_tip": preferences.get("auto_tip", True)
        }
    
    def set_payment_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Set user's payment preferences"""
        self.update_preferences(user_id, preferences)
    
    def get_notification_preferences(self, user_id: str) -> Dict[str, bool]:
        """Get user's notification preferences"""
        preferences = self.get_preferences(user_id)
        return preferences.get("notification_preferences", {
            "order_updates": True,
            "promotions": True,
            "delivery_alerts": True
        })
    
    def set_notification_preferences(self, user_id: str, preferences: Dict[str, bool]):
        """Set user's notification preferences"""
        self.update_preferences(user_id, {"notification_preferences": preferences})
    
    def cleanup_old_data(self, days_old: int = 90):
        """Clean up old user data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cutoff_str = cutoff_date.isoformat()
            
            # Clean up old order history
            for user_id, orders in self.order_history.items():
                self.order_history[user_id] = [
                    order for order in orders 
                    if order.get("order_date", "") > cutoff_str
                ]
            
            self._save_preferences()
            logger.info(f"Cleaned up user data older than {days_old} days")
        except Exception as e:
            logger.error(f"Error cleaning up old data: {str(e)}")
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            order_history = self.get_order_history(user_id)
            
            if not order_history:
                return {"total_orders": 0, "total_spent": 0, "favorite_cuisine": ""}
            
            total_orders = len(order_history)
            total_spent = sum(order.get("total_price", 0) for order in order_history)
            
            # Find favorite cuisine
            cuisine_counts = {}
            for order in order_history:
                cuisine = order.get("restaurant", {}).get("cuisine_type", "")
                if cuisine:
                    cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
            
            favorite_cuisine = max(cuisine_counts.items(), key=lambda x: x[1])[0] if cuisine_counts else ""
            
            return {
                "total_orders": total_orders,
                "total_spent": total_spent,
                "favorite_cuisine": favorite_cuisine,
                "average_order_value": total_spent / total_orders if total_orders > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            return {}
