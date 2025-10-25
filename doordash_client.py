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
        # DoorDash Drive API configuration
        self.access_key = os.getenv("DOORDASH_ACCESS_KEY", "")
        self.base_url = os.getenv("DOORDASH_BASE_URL", "https://openapi.doordash.com")
        
        # Drive API endpoints
        self.endpoints = {
            "create_delivery": "/drive/v2/deliveries",
            "get_delivery": "/drive/v2/deliveries/{delivery_id}",
            "update_delivery": "/drive/v2/deliveries/{delivery_id}",
            "cancel_delivery": "/drive/v2/deliveries/{delivery_id}/cancel"
        }
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make authenticated request to DoorDash Drive API"""
        headers = {
            "Authorization": f"Bearer {self.access_key}",
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
        Note: Drive API doesn't have restaurant search - this uses mock data
        """
        try:
            # Drive API doesn't provide restaurant search functionality
            # Return mock data for demonstration
            return self._get_mock_restaurants(query)
            
        except Exception as e:
            logger.error(f"Error searching restaurants: {str(e)}")
            return self._get_mock_restaurants(query)
    
    async def get_menu_items(self, restaurant_id: str) -> List[Dict]:
        """
        Get menu items for a specific restaurant
        Note: Drive API doesn't have menu functionality - this uses mock data
        """
        try:
            # Drive API doesn't provide menu functionality
            # Return mock data for demonstration
            return self._get_mock_menu_items(restaurant_id)
            
        except Exception as e:
            logger.error(f"Error getting menu items: {str(e)}")
            return self._get_mock_menu_items(restaurant_id)
    
    async def create_delivery(self, pickup_address: str, dropoff_address: str, pickup_phone: str, dropoff_phone: str, external_delivery_id: str) -> Dict:
        """
        Create a new delivery using DoorDash Drive API
        """
        try:
            # For demo purposes, return mock response if no access key
            if not self.access_key:
                return self._get_mock_delivery_response(external_delivery_id)
            
            delivery_data = {
                "external_delivery_id": external_delivery_id,
                "pickup_address": pickup_address,
                "pickup_phone_number": pickup_phone,
                "dropoff_address": dropoff_address,
                "dropoff_phone_number": dropoff_phone
            }
            
            response = await self._make_request("POST", self.endpoints["create_delivery"], data=delivery_data)
            return {
                "success": True,
                "delivery_id": response.get("id"),
                "external_delivery_id": response.get("external_delivery_id"),
                "status": response.get("delivery_status"),
                "estimated_delivery": response.get("estimated_delivery_time")
            }
            
        except Exception as e:
            logger.error(f"Error creating delivery: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_delivery_status(self, delivery_id: str) -> Dict:
        """
        Get the status of a delivery
        """
        try:
            if not self.access_key:
                return self._get_mock_delivery_status(delivery_id)
            
            endpoint = self.endpoints["get_delivery"].format(delivery_id=delivery_id)
            response = await self._make_request("GET", endpoint)
            return response
            
        except Exception as e:
            logger.error(f"Error getting delivery status: {str(e)}")
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
    
    def _get_mock_delivery_response(self, external_delivery_id: str) -> Dict:
        """Mock delivery response for testing"""
        estimated_delivery = (datetime.now() + timedelta(minutes=30)).isoformat()
        
        return {
            "success": True,
            "delivery_id": f"DELIVERY-{int(datetime.now().timestamp())}",
            "external_delivery_id": external_delivery_id,
            "status": "delivery_created",
            "estimated_delivery": estimated_delivery
        }
    
    def _get_mock_delivery_status(self, delivery_id: str) -> Dict:
        """Mock delivery status for testing"""
        return {
            "delivery_id": delivery_id,
            "status": "enroute_to_pickup",
            "estimated_delivery": (datetime.now() + timedelta(minutes=25)).isoformat(),
            "pickup_address": "1000 4th Ave, Seattle, WA, 98104",
            "dropoff_address": "1201 3rd Ave, Seattle, WA, 98101"
        }
    
    def _get_mock_delivery_quote(self) -> Dict:
        """Mock delivery quote for testing"""
        return {
            "delivery_fee": 2.99,
            "estimated_delivery_time": "25-35 min",
            "minimum_order": 10.00
        }
