from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.schemas import UserCreate, UserResponse, Token, UserOTPRequest, UserOTPVerify
from app.crud import users as users_crud
from app.auth.auth import create_access_token
from app.services.sms_service import SMSService
from datetime import timedelta
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
sms_service = SMSService()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists with the same mobile number
    db_user = users_crud.get_user_by_mobile(db, user.mobile)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered"
        )
    
    # Create new user
    return users_crud.create_user(db, user)

@router.post("/request-otp", status_code=status.HTTP_200_OK)
def request_otp(request: UserOTPRequest, db: Session = Depends(get_db)):
    """Request OTP for login/signup"""
    # Check if user exists
    user = users_crud.get_user_by_mobile(db, request.mobile)
    
    # If user doesn't exist, create a new one
    if not user:
        user = users_crud.create_user(db, UserCreate(
            name=f"User_{request.mobile}",  # Default name
            mobile=request.mobile,
            role="user"
        ))
    
    # Create OTP for this user
    otp_login = users_crud.create_otp_login(db, user.id)
    
    # Send OTP via SMS (mocked in development)
    try:
        # In production, uncomment the following to send actual SMS
        # sms_service.send_otp_sms(request.mobile, otp_login.otp_code)
        
        # In development, just log the OTP
        print(f"[DEV] OTP for {request.mobile}: {otp_login.otp_code}")
    except Exception as e:
        # Log the error but don't expose details to client
        print(f"SMS sending error: {str(e)}")
    
    return {"message": "OTP sent successfully", "dev_otp": otp_login.otp_code}

@router.post("/verify-otp", response_model=Token)
def verify_otp_handler(request: UserOTPVerify, db: Session = Depends(get_db)):
    """Verify OTP and get access token"""
    # Verify OTP
    user = users_crud.verify_otp(db, request.mobile, request.otp_code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP or OTP expired"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
