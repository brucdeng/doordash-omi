"""
OMI DoorDash Ordering App
Voice-activated food delivery ordering with OMI devices
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from doordash_client import DoorDashClient
from voice_processor import VoiceProcessor
from order_manager import OrderManager
from user_preferences import UserPreferences

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="OMI DoorDash Ordering", version="1.0.0")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize components
doordash_client = DoorDashClient()
voice_processor = VoiceProcessor()
order_manager = OrderManager()
user_preferences = UserPreferences()

# Pydantic models
class VoiceTranscript(BaseModel):
    segments: List[str]
    user_id: str
    session_id: str

class OrderRequest(BaseModel):
    restaurant_id: str
    items: List[Dict[str, Any]]
    delivery_address: str
    user_id: str

class OrderConfirmation(BaseModel):
    order_id: str
    total_price: float
    estimated_delivery: str
    restaurant_name: str

# Routes
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """Homepage with order history and preferences"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "OMI DoorDash Ordering"
    })

@app.get("/auth")
async def start_auth():
    """Start DoorDash OAuth flow"""
    # For now, redirect to test page since we're using API keys
    return RedirectResponse(url="/test")

@app.get("/test", response_class=HTMLResponse)
async def test_interface(request: Request):
    """Test interface for voice commands"""
    return templates.TemplateResponse("test.html", {
        "request": request,
        "title": "Test Voice Commands"
    })

@app.post("/webhook")
async def process_voice_command(transcript: VoiceTranscript):
    """
    Process voice commands from OMI device
    Handles: "Order a pepperoni pizza from the closest highly rated place"
    """
    try:
        logger.info(f"Processing voice command: {transcript.segments}")
        
        # Detect if this is a food ordering command
        if not voice_processor.is_food_order_command(transcript.segments):
            return {"status": "ignored", "message": "Not a food ordering command"}
        
        # Process the voice command
        order_intent = voice_processor.extract_order_intent(transcript.segments)
        
        if not order_intent:
            return {"status": "error", "message": "Could not understand order"}
        
        # Search for restaurants
        restaurants = await doordash_client.search_restaurants(
            query=order_intent.get("food_item", ""),
            location=order_intent.get("location", "")
        )
        
        if not restaurants:
            return {"status": "error", "message": "No restaurants found"}
        
        # Get user preferences for restaurant selection
        preferred_restaurant = user_preferences.get_preferred_restaurant(
            restaurants, transcript.user_id
        )
        
        # Get menu items
        menu_items = await doordash_client.get_menu_items(
            restaurant_id=preferred_restaurant["id"]
        )
        
        # Find matching items
        matching_items = voice_processor.find_matching_menu_items(
            order_intent, menu_items
        )
        
        if not matching_items:
            return {"status": "error", "message": "No matching menu items found"}
        
        # Create order summary
        order_summary = {
            "restaurant": preferred_restaurant,
            "items": matching_items,
            "estimated_total": sum(item["price"] for item in matching_items),
            "user_id": transcript.user_id,
            "session_id": transcript.session_id
        }
        
        # Store pending order
        order_manager.store_pending_order(transcript.session_id, order_summary)
        
        return {
            "status": "success",
            "message": "Order ready for confirmation",
            "order_summary": order_summary
        }
        
    except Exception as e:
        logger.error(f"Error processing voice command: {str(e)}")
        return {"status": "error", "message": "Failed to process order"}

@app.post("/confirm-order")
async def confirm_order(request: Request):
    """Confirm and place the order"""
    try:
        data = await request.json()
        session_id = data.get("session_id")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID required")
        
        # Get pending order
        pending_order = order_manager.get_pending_order(session_id)
        if not pending_order:
            raise HTTPException(status_code=404, detail="No pending order found")
        
        # Get user delivery address
        user_id = pending_order["user_id"]
        delivery_address = user_preferences.get_delivery_address(user_id)
        
        if not delivery_address:
            return {
                "status": "error",
                "message": "No delivery address set. Please set your address first."
            }
        
        # Place the order
        order_result = await doordash_client.create_order(
            restaurant_id=pending_order["restaurant"]["id"],
            items=pending_order["items"],
            delivery_address=delivery_address,
            user_id=user_id
        )
        
        if order_result["success"]:
            # Store successful order
            order_manager.store_completed_order(session_id, order_result)
            
            # Update user preferences
            user_preferences.update_order_history(user_id, pending_order)
            
            return {
                "status": "success",
                "message": "Order placed successfully!",
                "order_id": order_result["order_id"],
                "estimated_delivery": order_result["estimated_delivery"]
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to place order: {order_result['error']}"
            }
            
    except Exception as e:
        logger.error(f"Error confirming order: {str(e)}")
        return {"status": "error", "message": "Failed to confirm order"}

@app.get("/order-status/{order_id}")
async def get_order_status(order_id: str):
    """Get the status of an order"""
    try:
        status = await doordash_client.get_order_status(order_id)
        return {"status": "success", "order_status": status}
    except Exception as e:
        logger.error(f"Error getting order status: {str(e)}")
        return {"status": "error", "message": "Failed to get order status"}

@app.post("/set-preferences")
async def set_user_preferences(request: Request):
    """Set user preferences (delivery address, dietary restrictions, etc.)"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        preferences = data.get("preferences", {})
        
        user_preferences.update_preferences(user_id, preferences)
        
        return {"status": "success", "message": "Preferences updated"}
    except Exception as e:
        logger.error(f"Error setting preferences: {str(e)}")
        return {"status": "error", "message": "Failed to update preferences"}

@app.get("/user-preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """Get user preferences"""
    try:
        preferences = user_preferences.get_preferences(user_id)
        return {"status": "success", "preferences": preferences}
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        return {"status": "error", "message": "Failed to get preferences"}

@app.get("/order-history/{user_id}")
async def get_order_history(user_id: str):
    """Get user's order history"""
    try:
        history = user_preferences.get_order_history(user_id)
        return {"status": "success", "order_history": history}
    except Exception as e:
        logger.error(f"Error getting order history: {str(e)}")
        return {"status": "error", "message": "Failed to get order history"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
