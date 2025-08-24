from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.schemas import UserCreate, UserResponse, Token, UserOTPRequest, UserOTPVerify
from app.crud import users as users_crud
from app.auth.auth import create_access_token, authenticate_user_with_password
from app.services.sms_service import SMSService
from datetime import timedelta
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
sms_service = SMSService()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user - Only for normal users"""
    # Prevent admin/super_admin registration through normal signup
    if user.role in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users cannot be created through normal signup. Contact super admin."
        )
    
    # Force role to be 'user' for normal signup
    user.role = "user"
    
    # Check if user already exists with the same mobile number
    db_user = users_crud.get_user_by_mobile(db, user.mobile)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered"
        )
    
    # Check if email already exists (if provided)
    if user.email:
        existing_email_user = users_crud.get_user_by_email(db, user.email)
        if existing_email_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    return users_crud.create_user(db, user)

@router.post("/request-otp", status_code=status.HTTP_200_OK)
def request_otp(request: UserOTPRequest, db: Session = Depends(get_db)):
    """Request OTP for login/signup - Only for normal users"""
    # Check if user exists
    user = users_crud.get_user_by_mobile(db, request.mobile)
    
    # If user doesn't exist, create a new one with 'user' role
    if not user:
        user = users_crud.create_user(db, UserCreate(
            name=f"User_{request.mobile}",  # Default name
            mobile=request.mobile,
            role="user"  # Only normal users can use OTP login
        ))
    
    # Check if user is admin or super_admin - they should use password login
    if user.role in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users must login with email and password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending approval. Please contact admin."
        )
    
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
    """Verify OTP and get access token - Only for normal users"""
    # Verify OTP
    user = users_crud.verify_otp(db, request.mobile, request.otp_code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP or OTP expired"
        )
    
    # Double check - ensure user is not admin/super_admin
    if user.role in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users must login with email and password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending approval. Please contact admin."
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/admin-login", response_model=Token)
def admin_login_with_password(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with email and password - Only for admin and super_admin"""
    
    # Authenticate user using email and password
    user = authenticate_user_with_password(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Ensure user is admin or super_admin
    if user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This login is only for admin users. Normal users should use OTP login."
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your admin account is deactivated. Contact super admin."
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Token endpoint for OAuth2 compatibility - redirects to admin-login"""
    return admin_login_with_password(form_data, db)
