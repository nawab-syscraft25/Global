"""
Pydantic models that match the ideal database schema structure
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Union
from datetime import datetime
from decimal import Decimal
from enum import Enum

# ==============================
# Enum Classes for Validation
# ==============================
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    CREATED = "created"
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"

# ==============================
# Users & Authentication Schemas
# ==============================
class UserBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    mobile: str
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    role: Optional[UserRole] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserOTPRequest(BaseModel):
    mobile: str

class UserOTPVerify(BaseModel):
    mobile: str
    otp_code: str

class OTPLoginBase(BaseModel):
    user_id: int
    otp_code: str
    is_verified: bool = False
    expires_at: datetime

class OTPLoginCreate(OTPLoginBase):
    pass

class OTPLoginResponse(OTPLoginBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# ==============================
# Pujas & Images Schemas
# ==============================
class PujaBase(BaseModel):
    name: str
    description: Optional[str] = None

class PujaCreate(PujaBase):
    pass

class PujaUpdate(PujaBase):
    pass

class PujaResponse(PujaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PujaImageBase(BaseModel):
    puja_id: int
    image_url: str

class PujaImageCreate(PujaImageBase):
    pass

class PujaImageResponse(PujaImageBase):
    id: int

    class Config:
        orm_mode = True

# ==============================
# Global Plans & Mappings Schemas
# ==============================
class PlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    actual_price: Decimal
    discounted_price: Optional[Decimal] = None

class PlanCreate(PlanBase):
    pass

class PlanUpdate(PlanBase):
    pass

class PlanResponse(PlanBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class PujaPlanBase(BaseModel):
    puja_id: int
    plan_id: int

class PujaPlanCreate(PujaPlanBase):
    pass

class PujaPlanResponse(PujaPlanBase):
    id: int

    class Config:
        orm_mode = True

# ==============================
# Global Chadawas & Mappings Schemas
# ==============================
class ChadawaBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    price: Decimal
    requires_note: bool = False

class ChadawaCreate(ChadawaBase):
    pass

class ChadawaUpdate(ChadawaBase):
    pass

class ChadawaResponse(ChadawaBase):
    id: int

    class Config:
        orm_mode = True

class PujaChadawaBase(BaseModel):
    puja_id: int
    chadawa_id: int

class PujaChadawaCreate(PujaChadawaBase):
    pass

class PujaChadawaResponse(PujaChadawaBase):
    id: int

    class Config:
        orm_mode = True

# ==============================
# Bookings Schemas
# ==============================
class BookingBase(BaseModel):
    user_id: int
    puja_id: Optional[int] = None
    plan_id: Optional[int] = None
    booking_date: datetime = Field(default_factory=datetime.now)
    status: BookingStatus = BookingStatus.PENDING
    puja_link: Optional[str] = None

class BookingCreate(BaseModel):
    puja_id: Optional[int] = None
    plan_id: Optional[int] = None
    booking_date: Optional[datetime] = None
    chadawa_selections: Optional[List[Dict[str, Union[int, str]]]] = []  # List of {chadawa_id: int, note: Optional[str]}

class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    puja_link: Optional[str] = None

class BookingResponse(BookingBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class BookingChadawaBase(BaseModel):
    booking_id: int
    chadawa_id: Optional[int] = None
    note: Optional[str] = None

class BookingChadawaCreate(BookingChadawaBase):
    pass

class BookingChadawaResponse(BookingChadawaBase):
    id: int

    class Config:
        orm_mode = True

# ==============================
# Payments (Razorpay Integration) Schemas
# ==============================
class PaymentBase(BaseModel):
    booking_id: int
    razorpay_order_id: str
    amount: Decimal
    currency: str = "INR"
    status: PaymentStatus = PaymentStatus.CREATED

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    status: Optional[PaymentStatus] = None

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class PaymentResponse(PaymentBase):
    id: int
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ==============================
# Complex Response Schemas with Relationships
# ==============================
class PujaWithDetails(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    images: List[PujaImageResponse] = []
    plans: List[PlanResponse] = []
    chadawas: List[ChadawaResponse] = []

    class Config:
        orm_mode = True

class BookingWithDetails(BookingResponse):
    user: UserResponse
    puja: Optional[PujaResponse] = None
    plan: Optional[PlanResponse] = None
    chadawas: List[BookingChadawaResponse] = []
    payment: Optional[PaymentResponse] = None

    class Config:
        orm_mode = True

# ==============================
# Authentication & Token Schemas
# ==============================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None
    email: Optional[str] = None

# ==============================
# API Response Schemas
# ==============================
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None

class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    size: int
    pages: int

# ==============================
# Validation Functions
# ==============================
@validator('mobile')
def validate_mobile(cls, v):
    if not v or len(v) < 10:
        raise ValueError('Mobile number must be at least 10 digits')
    return v

# Apply mobile validator to relevant schemas
UserBase.mobile = Field(..., regex=r'^\+?[0-9]{10,15}$')
UserOTPRequest.mobile = Field(..., regex=r'^\+?[0-9]{10,15}$')
UserOTPVerify.mobile = Field(..., regex=r'^\+?[0-9]{10,15}$')
