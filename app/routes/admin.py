from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.schemas import BookingResponse, PaymentResponse
from app.crud import bookings as bookings_crud
from app.crud import payments as payments_crud
from app.auth.auth import get_admin_user
from app.models.models import User

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/bookings", response_model=List[BookingResponse])
def get_all_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get list of all bookings (admin only)"""
    return bookings_crud.get_all_bookings(db, skip, limit)

@router.get("/payments", response_model=List[PaymentResponse])
def get_all_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get list of all payments (admin only)"""
    return payments_crud.get_all_payments(db, skip, limit)
