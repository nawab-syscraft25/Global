from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.schemas import BookingResponse, PaymentResponse, UserResponse, UserUpdate, UserCreate
from app.crud import bookings as bookings_crud
from app.crud import payments as payments_crud
from app.crud import users as users_crud
from app.auth.auth import get_admin_user, get_super_admin_user
from app.models.models import User

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/bookings", response_model=List[BookingResponse])
def admin_get_all_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get list of all bookings (admin only)"""
    return bookings_crud.get_all_bookings(db, skip, limit)

@router.get("/payments", response_model=List[PaymentResponse])
def admin_get_all_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get list of all payments (admin only)"""
    return payments_crud.get_all_payments(db, skip, limit)

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get list of all users (admin only)"""
    return users_crud.get_users(db, skip, limit)

@router.put("/users/{user_id}/approve", response_model=UserResponse)
def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Approve a user (admin only)"""
    user = users_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user to active
    updated_user = users_crud.update_user(db, user_id, {"is_active": True})
    return updated_user

@router.put("/users/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Deactivate a user (admin only)"""
    user = users_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deactivating super admin
    if user.role == "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate super admin"
        )
    
    # Update user to inactive
    updated_user = users_crud.update_user(db, user_id, {"is_active": False})
    return updated_user

@router.put("/users/{user_id}/verify-email", response_model=UserResponse)
def verify_user_email(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Verify user's email (admin only)"""
    user = users_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user email verification status
    updated_user = users_crud.update_user(db, user_id, {"email_verified": True})
    return updated_user

@router.post("/create-admin", response_model=UserResponse)
def create_admin_user(
    admin_user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin_user)
):
    """Create admin user - Only super admin can create admin users"""
    # Only allow super admin to create admin users
    if admin_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint is only for creating admin users"
        )
    
    # Only super admin can create other super admins
    if admin_user.role == "super_admin" and current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can create other super admins"
        )
    
    # Check if email already exists
    if admin_user.email:
        existing_user = users_crud.get_user_by_email(db, admin_user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check if mobile already exists
    existing_mobile_user = users_crud.get_user_by_mobile(db, admin_user.mobile)
    if existing_mobile_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered"
        )
    
    # Ensure password is provided for admin users
    if not admin_user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required for admin users"
        )
    
    # Create admin user
    return users_crud.create_user(db, admin_user)
