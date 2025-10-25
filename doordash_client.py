"""
DoorDash API Client
Handles all DoorDash API interactions for restaurant search, menu items, and order placement
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DoorDashClient:
    def __init__(self):
        # DoorDash API configuration
        self.api_key = os.getenv("DOORDASH_API_KEY", "")
        self.base_url = os.getenv("DOORDASH_BASE_URL", "https://openapi.doordash.com")
        self.client_id = os.getenv("DOORDASH_CLIENT_ID", "")
        self.client_secret = os.getenv("DOORDASH_CLIENT_SECRET", "")
        
        # API endpoints
        self.endpoints = {
            "search_restaurants": "/v2/restaurants/search",
            "get_menu": "/v2/restaurants/{restaurant_id}/menu",
            "create_order": "/v2/orders",
            "get_order": "/v2/orders/{order_id}",
            "get_delivery_quote": "/v2/delivery_quotes"
        }
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make authenticated request to DoorDash API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Request failed: {str(e)}")
                raise
    
    async def search_restaurants(self, query: str, location: str = "", limit: int = 10) -> List[Dict]:
        """
        Search for restaurants based on food item and location
        """
        try:
            # For demo purposes, return mock data if no API key
            if not self.api_key:
                return self._get_mock_restaurants(query)
            
            params = {
                "query": query,
                "location": location,
                "limit": limit
            }
            
            response = await self._make_request("GET", self.endpoints["search_restaurants"], params=params)
            return response.get("restaurants", [])
            
        except Exception as e:
            logger.error(f"Error searching restaurants: {str(e)}")
            # Return mock data as fallback
            return self._get_mock_restaurants(query)
    
    async def get_menu_items(self, restaurant_id: str) -> List[Dict]:
        """
        Get menu items for a specific restaurant
        """
        try:
            # For demo purposes, return mock data if no API key
            if not self.api_key:
                return self._get_mock_menu_items(restaurant_id)
            
            endpoint = self.endpoints["get_menu"].format(restaurant_id=restaurant_id)
            response = await self._make_request("GET", endpoint)
            return response.get("menu_items", [])
            
        except Exception as e:
            logger.error(f"Error getting menu items: {str(e)}")
            # Return mock data as fallback
            return self._get_mock_menu_items(restaurant_id)
    
    async def create_order(self, restaurant_id: str, items: List[Dict], delivery_address: str, user_id: str) -> Dict:
        """
        Create a new order
        """
        try:
            # For demo purposes, return mock response if no API key
            if not self.api_key:
                return self._get_mock_order_response(restaurant_id, items)
            
            order_data = {
                "restaurant_id": restaurant_id,
                "items": items,
                "delivery_address": delivery_address,
                "user_id": user_id,
                "external_delivery_id": f"OMI-{user_id}-{int(datetime.now().timestamp())}"
            }
            
            response = await self._make_request("POST", self.endpoints["create_order"], data=order_data)
            return {
                "success": True,
                "order_id": response.get("order_id"),
                "estimated_delivery": response.get("estimated_delivery"),
                "total_price": response.get("total_price")
            }
            
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_order_status(self, order_id: str) -> Dict:
        """
        Get the status of an order
        """
        try:
            if not self.api_key:
                return self._get_mock_order_status(order_id)
            
            endpoint = self.endpoints["get_order"].format(order_id=order_id)
            response = await self._make_request("GET", endpoint)
            return response
            
        except Exception as e:
            logger.error(f"Error getting order status: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_delivery_quote(self, restaurant_id: str, delivery_address: str) -> Dict:
        """
        Get delivery quote for an order
        """
        try:
            if not self.api_key:
                return self._get_mock_delivery_quote()
            
            data = {
                "restaurant_id": restaurant_id,
                "delivery_address": delivery_address
            }
            
            response = await self._make_request("POST", self.endpoints["get_delivery_quote"], data=data)
            return response
            
        except Exception as e:
            logger.error(f"Error getting delivery quote: {str(e)}")
            return {"error": str(e)}
    
    def _get_mock_restaurants(self, query: str) -> List[Dict]:
        """Mock restaurant data for testing"""
        return [
            {
                "id": "rest_1",
                "name": "Tony's Pizza Palace",
                "rating": 4.5,
                "delivery_time": "25-35 min",
                "delivery_fee": 2.99,
                "cuisine_type": "Italian",
                "address": "123 Main St, City, State",
                "phone": "+1-555-0123",
                "is_open": True
            },
            {
                "id": "rest_2", 
                "name": "Mario's Italian Kitchen",
                "rating": 4.2,
                "delivery_time": "20-30 min",
                "delivery_fee": 1.99,
                "cuisine_type": "Italian",
                "address": "456 Oak Ave, City, State",
                "phone": "+1-555-0456",
                "is_open": True
            },
            {
                "id": "rest_3",
                "name": "Pizza Corner",
                "rating": 4.0,
                "delivery_time": "30-40 min", 
                "delivery_fee": 3.49,
                "cuisine_type": "Italian",
                "address": "789 Pine St, City, State",
                "phone": "+1-555-0789",
                "is_open": True
            }
        ]
    
    def _get_mock_menu_items(self, restaurant_id: str) -> List[Dict]:
        """Mock menu items for testing"""
        return [
            {
                "id": "item_1",
                "name": "Pepperoni Pizza",
                "description": "Classic pepperoni pizza with mozzarella cheese",
                "price": 12.99,
                "category": "Pizza",
                "is_available": True,
                "dietary_info": ["contains-dairy", "contains-gluten"]
            },
            {
                "id": "item_2",
                "name": "Margherita Pizza", 
                "description": "Fresh mozzarella, tomato sauce, and basil",
                "price": 11.99,
                "category": "Pizza",
                "is_available": True,
                "dietary_info": ["contains-dairy", "contains-gluten"]
            },
            {
                "id": "item_3",
                "name": "Caesar Salad",
                "description": "Fresh romaine lettuce with caesar dressing",
                "price": 8.99,
                "category": "Salad",
                "is_available": True,
                "dietary_info": ["contains-dairy", "contains-gluten"]
            }
        ]
    
    def _get_mock_order_response(self, restaurant_id: str, items: List[Dict]) -> Dict:
        """Mock order response for testing"""
        total_price = sum(item.get("price", 0) for item in items)
        estimated_delivery = (datetime.now() + timedelta(minutes=30)).isoformat()
        
        return {
            "success": True,
            "order_id": f"ORDER-{int(datetime.now().timestamp())}",
            "estimated_delivery": estimated_delivery,
            "total_price": total_price,
            "restaurant_id": restaurant_id
        }
    
    def _get_mock_order_status(self, order_id: str) -> Dict:
        """Mock order status for testing"""
        return {
            "order_id": order_id,
            "status": "confirmed",
            "estimated_delivery": (datetime.now() + timedelta(minutes=25)).isoformat(),
            "restaurant_name": "Tony's Pizza Palace"
        }
    
    def _get_mock_delivery_quote(self) -> Dict:
        """Mock delivery quote for testing"""
        return {
            "delivery_fee": 2.99,
            "estimated_delivery_time": "25-35 min",
            "minimum_order": 10.00
        }
