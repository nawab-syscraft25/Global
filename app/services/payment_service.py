import razorpay
import logging
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.crud import payments as payments_crud
from app.crud import bookings as bookings_crud
from app.models.models import PaymentStatus, BookingStatus, Payment
from app.schemas.schemas import PaymentCreate
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

class RazorpayService:
    def __init__(self):
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    def create_order(self, amount: float, currency: str = "INR", receipt: str = None) -> Dict[str, Any]:
        """
        Create a Razorpay order
        
        Args:
            amount: Amount in smallest currency unit (paise for INR)
            currency: Currency code (default: INR)
            receipt: Receipt ID
            
        Returns:
            Razorpay order object
        """
        try:
            # Convert amount to paise (Razorpay requires amount in smallest currency unit)
            amount_in_paise = int(amount * 100)
            
            data = {
                "amount": amount_in_paise,
                "currency": currency,
            }
            
            if receipt:
                data["receipt"] = receipt
                
            order = self.client.order.create(data=data)
            return order
        except Exception as e:
            logger.error(f"Error creating Razorpay order: {str(e)}")
            raise
    
    def verify_payment_signature(self, order_id: str, payment_id: str, signature: str) -> bool:
        """
        Verify Razorpay payment signature
        
        Args:
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            signature: Razorpay signature
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            # Verify the signature
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except Exception as e:
            logger.error(f"Error verifying Razorpay signature: {str(e)}")
            return False
    
    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """
        Get Razorpay payment details
        
        Args:
            payment_id: Razorpay payment ID
            
        Returns:
            Payment details
        """
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            logger.error(f"Error fetching Razorpay payment details: {str(e)}")
            raise

class PaymentService:
    def __init__(self):
        self.razorpay_service = RazorpayService()
        self.email_service = EmailService()
    
    def create_payment_order(self, db: Session, booking_id: int, user_id: int) -> Dict[str, Any]:
        """
        Create a payment order for a booking
        
        Args:
            db: Database session
            booking_id: Booking ID
            user_id: User ID
            
        Returns:
            Payment order details
        """
        # Get booking
        booking = bookings_crud.get_booking_by_id(db, booking_id)
        if not booking:
            raise ValueError("Booking not found")
        
        # Check if booking belongs to user
        if booking.user_id != user_id:
            raise ValueError("Not authorized to access this booking")
        
        # Calculate total amount
        total_amount = 0
        
        # Add plan amount if available
        if booking.plan:
            total_amount += float(booking.plan.discounted_price or booking.plan.actual_price)
        
        # Add chadawa amounts
        for booking_chadawa in booking.booking_chadawas:
            if booking_chadawa.chadawa:
                total_amount += float(booking_chadawa.chadawa.price)
        
        # Check if payment already exists
        existing_payment = payments_crud.get_payment_by_booking_id(db, booking_id)
        if existing_payment and existing_payment.status == PaymentStatus.SUCCESS.value:
            raise ValueError("Payment already completed for this booking")
        
        try:
            # Create Razorpay order
            order = self.razorpay_service.create_order(
                amount=total_amount,
                receipt=f"booking_{booking_id}"
            )
            
            # Save payment details
            payment_data = PaymentCreate(
                booking_id=booking_id,
                razorpay_order_id=order['id'],
                amount=total_amount,
                currency="INR",
                status=PaymentStatus.CREATED.value
            )
            
            if existing_payment:
                payments_crud.update_payment(db, existing_payment.id, payment_data)
                payment = existing_payment
            else:
                payment = payments_crud.create_payment(db, payment_data)
            
            # Return order details
            return {
                "order_id": order['id'],
                "amount": total_amount,
                "currency": "INR",
                "razorpay_key_id": settings.RAZORPAY_KEY_ID
            }
        
        except Exception as e:
            logger.error(f"Failed to create payment order: {str(e)}")
            raise ValueError(f"Failed to create payment order: {str(e)}")
    
    def verify_payment(
        self, 
        db: Session, 
        order_id: str, 
        payment_id: str, 
        signature: str,
        background_tasks = None
    ) -> Payment:
        """
        Verify and process a payment
        
        Args:
            db: Database session
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            signature: Razorpay signature
            background_tasks: FastAPI BackgroundTasks
            
        Returns:
            Updated payment object
        """
        # Get payment by order ID
        payment = payments_crud.get_payment_by_order_id(db, order_id)
        if not payment:
            raise ValueError("Payment not found")
        
        # Get booking
        booking = bookings_crud.get_booking_by_id(db, payment.booking_id)
        if not booking:
            raise ValueError("Booking not found")
        
        # Verify signature
        is_valid = self.razorpay_service.verify_payment_signature(order_id, payment_id, signature)
        
        if not is_valid:
            # Update payment status to failed
            payment = payments_crud.verify_payment(
                db, 
                order_id, 
                payment_id, 
                signature,
                PaymentStatus.FAILED.value
            )
            raise ValueError("Invalid payment signature")
        
        # Update payment status to success
        payment = payments_crud.verify_payment(
            db, 
            order_id, 
            payment_id, 
            signature,
            PaymentStatus.SUCCESS.value
        )
        
        # Update booking status
        booking = bookings_crud.update_booking(
            db,
            booking.id,
            {"status": BookingStatus.CONFIRMED.value}
        )
        
        # Send payment confirmation email if user has email
        if booking.user.email and background_tasks:
            # Get puja name
            puja_name = booking.puja.name if booking.puja else "Custom"
            
            # Prepare payment details for email
            payment_details = {
                "payment_id": payment_id,
                "order_id": order_id,
                "amount": float(payment.amount),
                "currency": payment.currency,
                "date": payment.updated_at.strftime("%Y-%m-%d %H:%M"),
                "puja_name": puja_name
            }
            
            # Send email in background
            background_tasks.add_task(
                self.email_service.send_payment_confirmation,
                booking.user.email,
                payment_details
            )
        
        return payment
    
    def get_user_payments(self, db: Session, user_id: int) -> List[Payment]:
        """
        Get all payments for a user
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of payment objects
        """
        # Get all bookings for user
        bookings = bookings_crud.get_user_bookings(db, user_id)
        
        # Get payments for each booking
        payments = []
        for booking in bookings:
            if booking.payment:
                payments.append(booking.payment)
        
        return payments
