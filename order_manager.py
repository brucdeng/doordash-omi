"""
Order Manager
Handles order storage, tracking, and management
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import os

logger = logging.getLogger(__name__)

class OrderManager:
    def __init__(self):
        self.storage_file = "orders.json"
        self.pending_orders = {}
        self.completed_orders = {}
        self._load_orders()
    
    def _load_orders(self):
        """Load orders from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.pending_orders = data.get("pending", {})
                    self.completed_orders = data.get("completed", {})
        except Exception as e:
            logger.error(f"Error loading orders: {str(e)}")
            self.pending_orders = {}
            self.completed_orders = {}
    
    def _save_orders(self):
        """Save orders to storage file"""
        try:
            data = {
                "pending": self.pending_orders,
                "completed": self.completed_orders,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving orders: {str(e)}")
    
    def store_pending_order(self, session_id: str, order_data: Dict[str, Any]):
        """Store a pending order"""
        try:
            order_data["created_at"] = datetime.now().isoformat()
            order_data["status"] = "pending"
            self.pending_orders[session_id] = order_data
            self._save_orders()
            logger.info(f"Stored pending order for session {session_id}")
        except Exception as e:
            logger.error(f"Error storing pending order: {str(e)}")
    
    def get_pending_order(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a pending order by session ID"""
        return self.pending_orders.get(session_id)
    
    def store_completed_order(self, session_id: str, order_result: Dict[str, Any]):
        """Store a completed order"""
        try:
            # Get the pending order data
            pending_order = self.pending_orders.get(session_id, {})
            
            # Create completed order record
            completed_order = {
                **pending_order,
                "order_id": order_result.get("order_id"),
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "estimated_delivery": order_result.get("estimated_delivery"),
                "total_price": order_result.get("total_price")
            }
            
            # Move from pending to completed
            if session_id in self.pending_orders:
                del self.pending_orders[session_id]
            
            self.completed_orders[session_id] = completed_order
            self._save_orders()
            logger.info(f"Stored completed order for session {session_id}")
        except Exception as e:
            logger.error(f"Error storing completed order: {str(e)}")
    
    def get_order_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get order history for a user"""
        try:
            user_orders = []
            for session_id, order in self.completed_orders.items():
                if order.get("user_id") == user_id:
                    user_orders.append(order)
            
            # Sort by completion date (newest first)
            user_orders.sort(key=lambda x: x.get("completed_at", ""), reverse=True)
            return user_orders[:limit]
        except Exception as e:
            logger.error(f"Error getting order history: {str(e)}")
            return []
    
    def get_recent_orders(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent orders for quick re-ordering"""
        return self.get_order_history(user_id, limit)
    
    def cancel_pending_order(self, session_id: str) -> bool:
        """Cancel a pending order"""
        try:
            if session_id in self.pending_orders:
                del self.pending_orders[session_id]
                self._save_orders()
                logger.info(f"Cancelled pending order for session {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cancelling pending order: {str(e)}")
            return False
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order by order ID"""
        try:
            # Search in completed orders
            for session_id, order in self.completed_orders.items():
                if order.get("order_id") == order_id:
                    return order
            
            # Search in pending orders
            for session_id, order in self.pending_orders.items():
                if order.get("order_id") == order_id:
                    return order
            
            return None
        except Exception as e:
            logger.error(f"Error getting order by ID: {str(e)}")
            return None
    
    def update_order_status(self, order_id: str, status: str, additional_data: Dict = None):
        """Update order status"""
        try:
            order = self.get_order_by_id(order_id)
            if order:
                order["status"] = status
                order["last_updated"] = datetime.now().isoformat()
                
                if additional_data:
                    order.update(additional_data)
                
                self._save_orders()
                logger.info(f"Updated order {order_id} status to {status}")
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")
    
    def get_pending_orders_count(self) -> int:
        """Get count of pending orders"""
        return len(self.pending_orders)
    
    def get_completed_orders_count(self) -> int:
        """Get count of completed orders"""
        return len(self.completed_orders)
    
    def cleanup_old_orders(self, days_old: int = 30):
        """Clean up old completed orders"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cutoff_str = cutoff_date.isoformat()
            
            # Remove old completed orders
            old_sessions = []
            for session_id, order in self.completed_orders.items():
                if order.get("completed_at", "") < cutoff_str:
                    old_sessions.append(session_id)
            
            for session_id in old_sessions:
                del self.completed_orders[session_id]
            
            if old_sessions:
                self._save_orders()
                logger.info(f"Cleaned up {len(old_sessions)} old orders")
        except Exception as e:
            logger.error(f"Error cleaning up old orders: {str(e)}")
    
    def get_order_statistics(self) -> Dict[str, Any]:
        """Get order statistics"""
        try:
            total_pending = len(self.pending_orders)
            total_completed = len(self.completed_orders)
            
            # Calculate total revenue from completed orders
            total_revenue = sum(
                order.get("total_price", 0) 
                for order in self.completed_orders.values()
            )
            
            return {
                "total_pending": total_pending,
                "total_completed": total_completed,
                "total_revenue": total_revenue,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting order statistics: {str(e)}")
            return {}
