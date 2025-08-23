from sqlalchemy.orm import Session
from app.models.models import Chadawa, PujaChadawa
from app.schemas.schemas import ChadawaCreate, ChadawaUpdate

def create_chadawa(db: Session, chadawa: ChadawaCreate):
    """Create a new chadawa"""
    db_chadawa = Chadawa(
        name=chadawa.name,
        description=chadawa.description,
        image_url=chadawa.image_url,
        price=chadawa.price,
        requires_note=chadawa.requires_note
    )
    db.add(db_chadawa)
    db.commit()
    db.refresh(db_chadawa)
    return db_chadawa

def get_chadawa_by_id(db: Session, chadawa_id: int):
    """Get chadawa by ID"""
    return db.query(Chadawa).filter(Chadawa.id == chadawa_id).first()

def get_chadawas_by_puja_id(db: Session, puja_id: int, skip: int = 0, limit: int = 100):
    """Get list of chadawas for a specific puja"""
    return db.query(Chadawa).join(
        PujaChadawa, PujaChadawa.chadawa_id == Chadawa.id
    ).filter(PujaChadawa.puja_id == puja_id).offset(skip).limit(limit).all()

def get_chadawas(db: Session, skip: int = 0, limit: int = 100):
    """Get list of all chadawas"""
    return db.query(Chadawa).offset(skip).limit(limit).all()

def update_chadawa(db: Session, chadawa_id: int, chadawa: ChadawaUpdate):
    """Update chadawa information"""
    db_chadawa = get_chadawa_by_id(db, chadawa_id)
    if not db_chadawa:
        return None
        
    # Update chadawa fields
    for key, value in chadawa.dict(exclude_unset=True).items():
        setattr(db_chadawa, key, value)
    
    db.commit()
    db.refresh(db_chadawa)
    return db_chadawa

def delete_chadawa(db: Session, chadawa_id: int):
    """Delete a chadawa"""
    db_chadawa = get_chadawa_by_id(db, chadawa_id)
    if not db_chadawa:
        return False
    
    db.delete(db_chadawa)
    db.commit()
    return True

def add_chadawa_to_puja(db: Session, puja_id: int, chadawa_id: int):
    """Associate a chadawa with a puja"""
    # Check if association already exists
    existing = db.query(PujaChadawa).filter(
        PujaChadawa.puja_id == puja_id,
        PujaChadawa.chadawa_id == chadawa_id
    ).first()
    
    if existing:
        return existing
    
    db_puja_chadawa = PujaChadawa(
        puja_id=puja_id,
        chadawa_id=chadawa_id
    )
    db.add(db_puja_chadawa)
    db.commit()
    db.refresh(db_puja_chadawa)
    return db_puja_chadawa

def remove_chadawa_from_puja(db: Session, puja_id: int, chadawa_id: int):
    """Remove a chadawa association from a puja"""
    db_puja_chadawa = db.query(PujaChadawa).filter(
        PujaChadawa.puja_id == puja_id,
        PujaChadawa.chadawa_id == chadawa_id
    ).first()
    
    if not db_puja_chadawa:
        return False
    
    db.delete(db_puja_chadawa)
    db.commit()
    return True
