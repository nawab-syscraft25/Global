from pydantic import BaseModel, EmailStr, Field, validator, root_validator
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
    mobile: str = Field(..., pattern=r'^\+?[0-9]{10,15}$')
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = Field(None, pattern=r'^\+?[0-9]{10,15}$')
    role: Optional[UserRole] = None

class UserOTPRequest(BaseModel):
    mobile: str = Field(..., pattern=r'^\+?[0-9]{10,15}$')

class UserOTPVerify(BaseModel):
    mobile: str = Field(..., pattern=r'^\+?[0-9]{10,15}$')
    otp_code: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==============================
# OTP Login Schemas
# ==============================
class OTPLoginBase(BaseModel):
    user_id: int
    otp_code: str
    is_verified: bool = False
    expires_at: datetime

class OTPLoginCreate(OTPLoginBase):
    pass

class OTPLogin(OTPLoginBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ==============================
# Pujas & Images Schemas
# ==============================
class OTPLoginBase(BaseModel):
    user_id: int
    otp_code: str
    is_verified: bool = False
    expires_at: datetime

class OTPLoginCreate(OTPLoginBase):
    pass

class OTPLogin(OTPLoginBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Puja Schemas
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
        from_attributes = True

# Puja Image Schemas
class PujaImageBase(BaseModel):
    puja_id: int
    image_url: str

class PujaImageCreate(PujaImageBase):
    pass

class PujaImage(PujaImageBase):
    id: int

    class Config:
        from_attributes = True

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
        from_attributes = True

# Puja Plan Schemas
class PujaPlanBase(BaseModel):
    puja_id: int
    plan_id: int

class PujaPlanCreate(PujaPlanBase):
    pass

class PujaPlan(PujaPlanBase):
    id: int

    class Config:
        from_attributes = True

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
        from_attributes = True

# Puja Chadawa Schemas
class PujaChadawaBase(BaseModel):
    puja_id: int
    chadawa_id: int

class PujaChadawaCreate(PujaChadawaBase):
    pass

class PujaChadawa(PujaChadawaBase):
    id: int

    class Config:
        from_attributes = True

# Booking Chadawa Schemas
class BookingChadawaBase(BaseModel):
    booking_id: int
    chadawa_id: int
    note: Optional[str] = None

class BookingChadawaCreate(BookingChadawaBase):
    pass

class BookingChadawa(BookingChadawaBase):
    id: int

    class Config:
        from_attributes = True

# ==============================
# Bookings Schemas
# ==============================
class BookingBase(BaseModel):
    user_id: int
    puja_id: Optional[int] = None
    plan_id: Optional[int] = None
    booking_date: datetime
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
    chadawas: List[BookingChadawa] = []

    class Config:
        from_attributes = True

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

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class PaymentUpdate(BaseModel):
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    status: Optional[PaymentStatus] = None

class PaymentResponse(PaymentBase):
    id: int
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==============================
# Complex Response Schemas with Relationships
# ==============================
class PujaWithDetails(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    images: List[PujaImage] = []
    plans: List[PlanResponse] = []
    chadawas: List[ChadawaResponse] = []

    class Config:
        from_attributes = True

class BookingWithDetails(BookingResponse):
    user: UserResponse
    puja: Optional[PujaResponse] = None
    plan: Optional[PlanResponse] = None
    payment: Optional[PaymentResponse] = None

    class Config:
        from_attributes = True

# ==============================
# Authentication & Token Schemas
# ==============================
# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None
    email: Optional[str] = None
