from sqlalchemy.orm import Session
from app.models.models import Payment
from app.schemas.schemas import PaymentCreate, PaymentUpdate
from datetime import datetime

def create_payment(db: Session, payment: PaymentCreate):
    """Create a new payment record"""
    db_payment = Payment(
        booking_id=payment.booking_id,
        razorpay_order_id=payment.razorpay_order_id,
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def get_payment_by_booking_id(db: Session, booking_id: int):
    """Get payment by booking ID"""
    return db.query(Payment).filter(Payment.booking_id == booking_id).first()

def get_payment_by_order_id(db: Session, order_id: str):
    """Get payment by Razorpay order ID"""
    return db.query(Payment).filter(Payment.razorpay_order_id == order_id).first()

def get_payment_by_id(db: Session, payment_id: int):
    """Get payment by ID"""
    return db.query(Payment).filter(Payment.id == payment_id).first()

def update_payment(db: Session, payment_id: int, payment_data: PaymentUpdate):
    """Update payment information"""
    db_payment = get_payment_by_id(db, payment_id)
    if not db_payment:
        return None
    
    # Update payment fields
    for key, value in payment_data.dict(exclude_unset=True).items():
        setattr(db_payment, key, value)
    
    db_payment.updated_at = datetime.now()
    db.commit()
    db.refresh(db_payment)
    return db_payment

def update_payment_status(db: Session, payment_id: int, status: str):
    """Update payment status"""
    db_payment = get_payment_by_id(db, payment_id)
    if not db_payment:
        return None
    
    db_payment.status = status
    db_payment.updated_at = datetime.now()
    db.commit()
    db.refresh(db_payment)
    return db_payment

def verify_payment(
    db: Session, 
    order_id: str, 
    payment_id: str, 
    signature: str, 
    status: str = "completed"
):
    """Verify and update payment after successful payment"""
    db_payment = get_payment_by_order_id(db, order_id)
    if not db_payment:
        return None
    
    db_payment.razorpay_payment_id = payment_id
    db_payment.razorpay_signature = signature
    db_payment.status = status
    db_payment.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_payment)
    return db_payment

def get_all_payments(db: Session, skip: int = 0, limit: int = 100):
    """Get list of all payments"""
    return db.query(Payment).offset(skip).limit(limit).all()

def get_payments_by_status(db: Session, status: str, skip: int = 0, limit: int = 100):
    """Get list of payments by status"""
    return db.query(Payment).filter(Payment.status == status).offset(skip).limit(limit).all()
