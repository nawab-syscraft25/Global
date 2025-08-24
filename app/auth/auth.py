from datetime import datetime, timedelta
from typing import Optional
import random
import string
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import get_db
from app.models.models import User, OTPLogin
from app.schemas.schemas import TokenData
from app.config import settings

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/admin-login")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OTP generation and verification functions
def generate_otp(length: int = 6) -> str:
    """Generate a random OTP of specified length"""
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(length))

def generate_otp_secret() -> str:
    """Generate a secret for OTP (placeholder for future TOTP implementation)"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))

def verify_otp(otp_code: str, stored_otp: str, expires_at: datetime) -> bool:
    """Verify if the provided OTP matches and hasn't expired"""
    if datetime.utcnow() > expires_at:
        return False
    return otp_code == stored_otp

# Password hashing and verification functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    if not hashed_password:
        return False
    
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        return result
    except Exception as e:
        return False

def get_password_hash(password: str) -> str:
    """Hash a password for storing in the database"""
    return pwd_context.hash(password)

def authenticate_user_with_password(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user using email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    
    # Check if user is active
    if not user.is_active:
        return None
    
    # Check if user has password
    if not user.password:
        return None
    
    # Verify password
    if not verify_password(password, user.password):
        return None
    
    return user

def authenticate_user(db: Session, mobile: str, otp_code: str) -> Optional[User]:
    """Authenticate user using mobile number and OTP"""
    # Find the most recent valid OTP for this user
    user = db.query(User).filter(User.mobile == mobile).first()
    if not user:
        return None
    
    otp_login = db.query(OTPLogin).filter(
        OTPLogin.user_id == user.id,
        OTPLogin.otp_code == otp_code,
        OTPLogin.is_verified == False,
        OTPLogin.expires_at > datetime.utcnow()
    ).first()
    
    if otp_login:
        # Mark OTP as verified
        otp_login.is_verified = True
        db.commit()
        return user
    return None

# Function to create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Function to get current user from token
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id, role=role)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user

# Function to check if user is admin or super admin
async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Function to check if user is super admin
async def get_super_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin permissions required"
        )
    return current_user

# Function to get current active user
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user - check if user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
