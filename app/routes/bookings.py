from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.schemas import BookingResponse, BookingCreate, BookingUpdate, BookingWithDetails
from app.crud import bookings as bookings_crud
from app.services.booking_service import BookingService
from app.auth.auth import get_current_user, get_admin_user
from app.models.models import User

router = APIRouter(tags=["Bookings"])
booking_service = BookingService()

# User routes
@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new booking"""
    # Override user_id with the current user's ID for security
    booking_data = booking.dict()
    booking_data["user_id"] = current_user.id
    
    try:
        return bookings_crud.create_booking(db, BookingCreate(**booking_data))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/bookings/{booking_id}", response_model=BookingWithDetails)
def get_booking(
    booking_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific booking by ID"""
    booking = bookings_crud.get_booking_by_id(db, booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Regular users can only view their own bookings
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this booking"
        )
    
    return booking

@router.get("/user/bookings", response_model=List[BookingResponse])
def get_user_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of bookings for the current user"""
    return bookings_crud.get_bookings_by_user_id(db, current_user.id, skip, limit)

@router.post("/bookings/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a booking"""
    # Check if booking exists and belongs to user
    booking = bookings_crud.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Regular users can only cancel their own bookings
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this booking"
        )
    
    cancelled_booking = bookings_crud.cancel_booking(db, booking_id)
    if not cancelled_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking cannot be cancelled"
        )
    
    return cancelled_booking

# Admin routes
@router.get("/admin/bookings", response_model=List[BookingWithDetails])
def get_all_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get list of all bookings (admin only)"""
    return bookings_crud.get_all_bookings(db, skip, limit)

@router.put("/admin/bookings/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int = Path(..., ge=1),
    booking_update: BookingUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update booking information (admin only)"""
    updated_booking = bookings_crud.update_booking(db, booking_id, booking_update)
    
    if not updated_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    return updated_booking
