from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.models import User, OTPLogin
from app.schemas.schemas import UserCreate, UserOTPRequest
from app.auth.auth import get_password_hash
import random
import string

def create_user(db: Session, user: UserCreate):
    """Create a new user"""
    # Determine if user should be active by default based on role
    is_active = user.role in ["super_admin", "admin"]
    
    # Hash password if provided
    hashed_password = None
    if user.password:
        hashed_password = get_password_hash(user.password)
    
    db_user = User(
        name=user.name,
        email=user.email,
        mobile=user.mobile,
        role=user.role,
        password=hashed_password,
        is_active=is_active,
        email_verified=False,  # Default to False, can be verified later
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_mobile(db: Session, mobile: str):
    """Get user by mobile number"""
    return db.query(User).filter(User.mobile == mobile).first()

def get_user_by_id(db: Session, user_id: int):
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get list of users"""
    return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user_data: dict):
    """Update user information"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
        
    # Update user fields
    for key, value in user_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    
    db_user.updated_at = datetime.now()
    db.commit()
    db.refresh(db_user)
    return db_user

def generate_otp(length=6):
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))

def create_otp_login(db: Session, user_id: int, expires_minutes: int = 10):
    """Create a new OTP login record"""
    # Delete any existing OTPs for this user
    db.query(OTPLogin).filter(OTPLogin.user_id == user_id).delete()
    
    otp_code = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=expires_minutes)
    
    db_otp = OTPLogin(
        user_id=user_id,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)
    return db_otp

def verify_otp(db: Session, mobile: str, otp_code: str):
    """Verify an OTP for a user"""
    user = get_user_by_mobile(db, mobile)
    if not user:
        return None
    
    db_otp = db.query(OTPLogin).filter(
        OTPLogin.user_id == user.id,
        OTPLogin.otp_code == otp_code,
        OTPLogin.expires_at > datetime.now(),
        OTPLogin.is_verified == False
    ).first()
    
    if db_otp:
        db_otp.is_verified = True
        db.commit()
        return user
    
    return None
