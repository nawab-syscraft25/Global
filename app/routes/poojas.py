from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.schemas import PoojaResponse, PoojaCreate, PoojaUpdate
from app.crud import poojas as poojas_crud
from app.auth.auth import get_current_active_user, get_admin_user
from app.models.models import User

router = APIRouter(tags=["Poojas"])

# Public routes
@router.get("/poojas", response_model=List[PoojaResponse])
def get_poojas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of all poojas"""
    return poojas_crud.get_poojas(db, skip, limit)

@router.get("/poojas/{pooja_id}", response_model=PoojaResponse)
def get_pooja(pooja_id: int, db: Session = Depends(get_db)):
    """Get a specific pooja by ID"""
    pooja = poojas_crud.get_pooja_by_id(db, pooja_id)
    if not pooja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pooja not found"
        )
    return pooja

# Admin routes
@router.post("/admin/poojas", response_model=PoojaResponse, status_code=status.HTTP_201_CREATED)
def create_pooja(
    pooja: PoojaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new pooja (admin only)"""
    return poojas_crud.create_pooja(db, pooja)

@router.put("/admin/poojas/{pooja_id}", response_model=PoojaResponse)
def update_pooja(
    pooja_id: int,
    pooja: PoojaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update a pooja (admin only)"""
    updated_pooja = poojas_crud.update_pooja(db, pooja_id, pooja)
    if not updated_pooja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pooja not found"
        )
    return updated_pooja

@router.delete("/admin/poojas/{pooja_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pooja(
    pooja_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete a pooja (admin only)"""
    success = poojas_crud.delete_pooja(db, pooja_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pooja not found"
        )
    return None
