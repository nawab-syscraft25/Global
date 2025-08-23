import logging
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Union
from decimal import Decimal

from app.models.models import Puja, Chadawa, Booking, User, Plan, BookingChadawa
from app.schemas.schemas import BookingCreate
from app.crud import bookings as bookings_crud
from app.crud import pujas as pujas_crud
from app.crud import chadawas as chadawas_crud
from app.services.sms_service import SMSService

logger = logging.getLogger(__name__)

class BookingService:
    def __init__(self):
        self.sms_service = SMSService()
    
    def calculate_total_amount(
        self, 
        db: Session, 
        plan_id: Optional[int] = None,
        puja_id: Optional[int] = None, 
        chadawa_selections: List[Dict[str, Union[int, str]]] = None
    ) -> Decimal:
        """
        Calculate the total amount for a booking
        
        Args:
            db: Database session
            plan_id: Plan ID
            puja_id: Puja ID
            chadawa_selections: List of chadawa selections with IDs and notes
            
        Returns:
            Total amount
        """
        total_amount = Decimal('0.00')
        
        # Get plan price if provided
        if plan_id:
            plan = pujas_crud.get_plan_by_id(db, plan_id)
            if not plan:
                raise ValueError(f"Plan with ID {plan_id} not found")
            
            # Use discounted price if available, otherwise use actual price
            price = plan.discounted_price if plan.discounted_price else plan.actual_price
            total_amount += price
        
        # Add chadawa prices if provided
        if chadawa_selections:
            for selection in chadawa_selections:
                chadawa_id = selection.get('chadawa_id')
                if chadawa_id:
                    chadawa = chadawas_crud.get_chadawa_by_id(db, chadawa_id)
                    if chadawa:
                        total_amount += chadawa.price
        
        return total_amount
    
    def create_booking(
        self, 
        db: Session, 
        booking_data: BookingCreate
    ) -> Booking:
        """
        Create a new booking
        
        Args:
            db: Database session
            booking_data: Booking data
            
        Returns:
            Created booking
        """
        # Create the booking first
        booking = bookings_crud.create_booking(db, booking_data)
        
        # Get user for notification
        user = db.query(User).filter(User.id == booking_data.user_id).first()
        
        # Get puja or plan name for notification
        service_name = ""
        if booking_data.puja_id:
            puja = db.query(Puja).filter(Puja.id == booking_data.puja_id).first()
            if puja:
                service_name = puja.name
        
        if booking_data.plan_id:
            plan = db.query(Plan).filter(Plan.id == booking_data.plan_id).first()
            if plan:
                service_name = plan.name
        
        # Send confirmation SMS
        if user:
            self.sms_service.send_booking_confirmation_sms(
                user.mobile, 
                str(booking.id), 
                service_name
            )
        
        return booking
    
    def add_chadawas_to_booking(
        self,
        db: Session,
        booking_id: int,
        chadawa_selections: List[Dict[str, Union[int, str]]]
    ) -> Booking:
        """
        Add chadawas to an existing booking
        
        Args:
            db: Database session
            booking_id: Booking ID
            chadawa_selections: List of chadawa selections with IDs and notes
            
        Returns:
            Updated booking
        """
        booking = bookings_crud.get_booking_by_id(db, booking_id)
        if not booking:
            raise ValueError(f"Booking with ID {booking_id} not found")
        
        for selection in chadawa_selections:
            chadawa_id = selection.get('chadawa_id')
            note = selection.get('note')
            
            if chadawa_id:
                bookings_crud.add_chadawa_to_booking(db, booking_id, chadawa_id, note)
        
        # Refresh booking after adding chadawas
        return bookings_crud.get_booking_by_id(db, booking_id)
