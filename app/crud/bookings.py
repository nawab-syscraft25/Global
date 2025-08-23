from sqlalchemy.orm import Session, joinedload
from app.models.models import Booking, BookingChadawa, Chadawa
from app.schemas.schemas import BookingCreate, BookingUpdate
from typing import List, Dict, Union

def create_booking(db: Session, booking: BookingCreate):
    """Create a new booking"""
    db_booking = Booking(
        user_id=booking.user_id,
        puja_id=booking.puja_id,
        plan_id=booking.plan_id,
        booking_date=booking.booking_date,
        status=booking.status,
        puja_link=booking.puja_link
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    # Add chadawas to booking if provided
    if booking.chadawa_selections:
        for selection in booking.chadawa_selections:
            chadawa_id = selection.get('chadawa_id')
            note = selection.get('note')
            
            booking_chadawa = BookingChadawa(
                booking_id=db_booking.id,
                chadawa_id=chadawa_id,
                note=note
            )
            db.add(booking_chadawa)
        
        db.commit()
        db.refresh(db_booking)
    
    return db_booking

def get_booking_by_id(db: Session, booking_id: int):
    """Get booking by ID with relationships loaded"""
    return db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.puja),
        joinedload(Booking.plan),
        joinedload(Booking.chadawas).joinedload(BookingChadawa.chadawa),
        joinedload(Booking.payment)
    ).filter(Booking.id == booking_id).first()

def get_bookings_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get list of bookings for a specific user with relationships loaded"""
    return db.query(Booking).options(
        joinedload(Booking.puja),
        joinedload(Booking.plan),
        joinedload(Booking.chadawas).joinedload(BookingChadawa.chadawa),
        joinedload(Booking.payment)
    ).filter(Booking.user_id == user_id).offset(skip).limit(limit).all()

def get_all_bookings(db: Session, skip: int = 0, limit: int = 100):
    """Get list of all bookings with relationships loaded"""
    return db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.puja),
        joinedload(Booking.plan),
        joinedload(Booking.chadawas).joinedload(BookingChadawa.chadawa),
        joinedload(Booking.payment)
    ).offset(skip).limit(limit).all()

def update_booking(db: Session, booking_id: int, booking_data: BookingUpdate):
    """Update booking information"""
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not db_booking:
        return None
    
    # Update booking fields
    for key, value in booking_data.dict(exclude_unset=True).items():
        setattr(db_booking, key, value)
    
    db.commit()
    db.refresh(db_booking)
    return db_booking

def cancel_booking(db: Session, booking_id: int):
    """Cancel a booking"""
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not db_booking:
        return None
    
    # Only allow cancellation of pending or confirmed bookings
    if db_booking.status in ["pending", "confirmed"]:
        db_booking.status = "cancelled"
        
        db.commit()
        db.refresh(db_booking)
        return db_booking
    
    return None

def add_chadawa_to_booking(db: Session, booking_id: int, chadawa_id: int, note: str = None):
    """Add a chadawa to an existing booking"""
    # Check if association already exists
    existing = db.query(BookingChadawa).filter(
        BookingChadawa.booking_id == booking_id,
        BookingChadawa.chadawa_id == chadawa_id
    ).first()
    
    if existing:
        # Update note if provided
        if note is not None:
            existing.note = note
            db.commit()
            db.refresh(existing)
        return existing
    
    db_booking_chadawa = BookingChadawa(
        booking_id=booking_id,
        chadawa_id=chadawa_id,
        note=note
    )
    db.add(db_booking_chadawa)
    db.commit()
    db.refresh(db_booking_chadawa)
    return db_booking_chadawa

def remove_chadawa_from_booking(db: Session, booking_id: int, chadawa_id: int):
    """Remove a chadawa from a booking"""
    db_booking_chadawa = db.query(BookingChadawa).filter(
        BookingChadawa.booking_id == booking_id,
        BookingChadawa.chadawa_id == chadawa_id
    ).first()
    
    if not db_booking_chadawa:
        return False
    
    db.delete(db_booking_chadawa)
    db.commit()
    return True
