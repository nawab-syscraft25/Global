"""
Supabase Payment Service for Global Pooja FastAPI Application
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from supabase.client import Client
from .client import get_supabase

class SupabasePaymentService:
    def __init__(self):
        self.supabase = get_supabase()
    
    async def create_payment(self, payment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new payment record in Supabase
        
        Args:
            payment_data: Dictionary containing payment information
            
        Returns:
            Payment record or None if failed
        """
        try:
            result = self.supabase.table('payments').insert({
                'booking_id': payment_data['booking_id'],
                'razorpay_order_id': payment_data['razorpay_order_id'],
                'amount': payment_data['amount'],
                'currency': payment_data.get('currency', 'INR'),
                'status': payment_data.get('status', 'created')
            }).execute()
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"Error creating payment: {e}")
            return None
    
    async def get_payment_by_order_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a payment by Razorpay order ID
        
        Args:
            order_id: Razorpay order ID
            
        Returns:
            Payment record or None if not found
        """
        try:
            result = self.supabase.table('payments').select('*').eq('razorpay_order_id', order_id).execute()
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"Error getting payment by order ID: {e}")
            return None
    
    async def get_payment_by_booking_id(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a payment by booking ID
        
        Args:
            booking_id: Booking ID
            
        Returns:
            Payment record or None if not found
        """
        try:
            result = self.supabase.table('payments').select('*').eq('booking_id', booking_id).execute()
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"Error getting payment by booking ID: {e}")
            return None
    
    async def verify_payment(self, order_id: str, payment_id: str, signature: str) -> Optional[Dict[str, Any]]:
        """
        Update payment after verification
        
        Args:
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            signature: Razorpay signature
            
        Returns:
            Updated payment record or None if failed
        """
        try:
            result = self.supabase.table('payments').update({
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature,
                'status': 'success',
                'updated_at': datetime.now().isoformat()
            }).eq('razorpay_order_id', order_id).execute()
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"Error verifying payment: {e}")
            return None
    
    async def get_user_payments(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all payments for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            List of payment records
        """
        try:
            # Join with bookings to get payments for the specific user
            result = self.supabase.table('payments').select(
                '*, bookings!inner(id, user_id)'
            ).eq('bookings.user_id', user_id).execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting user payments: {e}")
            return []
    
    async def get_all_payments(self) -> List[Dict[str, Any]]:
        """
        Get all payments (admin only)
        
        Returns:
            List of all payment records
        """
        try:
            result = self.supabase.table('payments').select('*').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting all payments: {e}")
            return []
    
    async def update_payment_status(self, payment_id: int, status: str) -> Optional[Dict[str, Any]]:
        """
        Update payment status
        
        Args:
            payment_id: Payment ID
            status: New status
            
        Returns:
            Updated payment record or None if failed
        """
        try:
            result = self.supabase.table('payments').update({
                'status': status,
                'updated_at': datetime.now().isoformat()
            }).eq('id', payment_id).execute()
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"Error updating payment status: {e}")
            return None
