from fastapi import APIRouter, Depends, HTTPException, status, Body, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List

from app.database import get_db
from app.schemas.schemas import PaymentResponse, PaymentCreate, PaymentVerify
from app.crud import payments as payments_crud
from app.services.payment_service import PaymentService
from app.auth.auth import get_current_active_user, get_admin_user
from app.models.models import User

router = APIRouter(prefix="/payments", tags=["Payments"])
payment_service = PaymentService()

@router.post("/create-order/{booking_id}", response_model=Dict)
def create_payment_order(
    booking_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a payment order for a booking"""
    try:
        payment_order = payment_service.create_payment_order(db, booking_id, current_user.id)
        return payment_order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/verify", response_model=PaymentResponse)
def verify_payment(
    payment_data: PaymentVerify,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Verify Razorpay payment signature"""
    try:
        payment = payment_service.verify_payment(
            db,
            payment_data.razorpay_order_id,
            payment_data.razorpay_payment_id,
            payment_data.razorpay_signature,
            background_tasks
        )
        return payment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/status/{booking_id}", response_model=PaymentResponse)
def get_payment_status(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get payment status for a booking"""
    # Get payment
    payment = payments_crud.get_payment_by_booking_id(db, booking_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found for this booking"
        )
    
    # Check if user is authorized to view this payment
    booking = payment.booking
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this payment"
        )
    
    return payment

@router.get("/user", response_model=List[PaymentResponse])
def get_user_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all payments for the current user"""
    return payment_service.get_user_payments(db, current_user.id)

@router.get("/admin", response_model=List[PaymentResponse])
def get_all_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all payments (admin only)"""
    return payments_crud.get_all_payments(db)
