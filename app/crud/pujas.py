from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from app.models.models import Puja, PujaImage, Plan, PujaPlan, Chadawa, PujaChadawa
from app.schemas.schemas import PujaCreate, PujaUpdate, PujaImageCreate, PlanCreate

def create_puja(db: Session, puja: PujaCreate):
    """Create a new puja"""
    db_puja = Puja(
        name=puja.name,
        description=puja.description
    )
    db.add(db_puja)
    db.commit()
    db.refresh(db_puja)
    return db_puja

def get_puja_by_id(db: Session, puja_id: int):
    """Get puja by ID with all relationships loaded"""
    return db.query(Puja).options(
        joinedload(Puja.images),
        joinedload(Puja.plans).joinedload(PujaPlan.plan),
        joinedload(Puja.chadawas).joinedload(PujaChadawa.chadawa)
    ).filter(Puja.id == puja_id).first()

def get_pujas(db: Session, skip: int = 0, limit: int = 100):
    """Get list of pujas"""
    return db.query(Puja).offset(skip).limit(limit).all()

def get_pujas_with_details(db: Session, skip: int = 0, limit: int = 100):
    """Get list of pujas with all relationships loaded"""
    return db.query(Puja).options(
        joinedload(Puja.images),
        joinedload(Puja.plans).joinedload(PujaPlan.plan),
        joinedload(Puja.chadawas).joinedload(PujaChadawa.chadawa)
    ).offset(skip).limit(limit).all()

def update_puja(db: Session, puja_id: int, puja: PujaUpdate):
    """Update puja information"""
    db_puja = db.query(Puja).filter(Puja.id == puja_id).first()
    if not db_puja:
        return None
        
    # Update puja fields
    for key, value in puja.dict(exclude_unset=True).items():
        setattr(db_puja, key, value)
    
    db.commit()
    db.refresh(db_puja)
    return db_puja

def delete_puja(db: Session, puja_id: int):
    """Delete a puja"""
    db_puja = db.query(Puja).filter(Puja.id == puja_id).first()
    if not db_puja:
        return False
    
    db.delete(db_puja)
    db.commit()
    return True

def add_puja_image(db: Session, image: PujaImageCreate):
    """Add an image to a puja"""
    db_image = PujaImage(
        puja_id=image.puja_id,
        image_url=image.image_url
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def delete_puja_image(db: Session, image_id: int):
    """Delete a puja image"""
    db_image = db.query(PujaImage).filter(PujaImage.id == image_id).first()
    if not db_image:
        return False
    
    db.delete(db_image)
    db.commit()
    return True

def create_plan(db: Session, plan: PlanCreate):
    """Create a new plan"""
    db_plan = Plan(
        name=plan.name,
        description=plan.description,
        image_url=plan.image_url,
        actual_price=Decimal(str(plan.actual_price)),
        discounted_price=Decimal(str(plan.discounted_price)) if plan.discounted_price is not None else None
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def get_plan_by_id(db: Session, plan_id: int):
    """Get plan by ID"""
    return db.query(Plan).filter(Plan.id == plan_id).first()

def get_plans(db: Session, skip: int = 0, limit: int = 100):
    """Get list of plans"""
    return db.query(Plan).offset(skip).limit(limit).all()

def add_plan_to_puja(db: Session, puja_id: int, plan_id: int):
    """Associate a plan with a puja"""
    # Check if association already exists
    existing = db.query(PujaPlan).filter(
        PujaPlan.puja_id == puja_id,
        PujaPlan.plan_id == plan_id
    ).first()
    
    if existing:
        return existing
    
    db_puja_plan = PujaPlan(
        puja_id=puja_id,
        plan_id=plan_id
    )
    db.add(db_puja_plan)
    db.commit()
    db.refresh(db_puja_plan)
    return db_puja_plan

def remove_plan_from_puja(db: Session, puja_id: int, plan_id: int):
    """Remove a plan association from a puja"""
    db_puja_plan = db.query(PujaPlan).filter(
        PujaPlan.puja_id == puja_id,
        PujaPlan.plan_id == plan_id
    ).first()
    
    if not db_puja_plan:
        return False
    
    db.delete(db_puja_plan)
    db.commit()
    return True
