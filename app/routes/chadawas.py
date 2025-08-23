from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.schemas import ChadawaResponse, ChadawaCreate, ChadawaUpdate
from app.crud import chadawas as chadawas_crud
from app.crud import pujas as pujas_crud
from app.auth.auth import get_current_user, get_admin_user
from app.models.models import User

router = APIRouter(tags=["Chadawas"])

# Public routes
@router.get("/chadawas", response_model=List[ChadawaResponse])
def get_all_chadawas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of all chadawas"""
    return chadawas_crud.get_chadawas(db, skip, limit)

@router.get("/pujas/{puja_id}/chadawas", response_model=List[ChadawaResponse])
def get_puja_chadawas(
    puja_id: int = Path(..., ge=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of chadawas for a specific puja"""
    # Check if puja exists
    puja = pujas_crud.get_puja_by_id(db, puja_id)
    if not puja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puja not found"
        )
    
    return chadawas_crud.get_chadawas_by_puja_id(db, puja_id, skip, limit)

# Admin routes
@router.post("/admin/chadawas", response_model=ChadawaResponse, status_code=status.HTTP_201_CREATED)
def create_chadawa(
    chadawa: ChadawaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new chadawa (admin only)"""
    return chadawas_crud.create_chadawa(db, chadawa)

@router.put("/admin/chadawas/{chadawa_id}", response_model=ChadawaResponse)
def update_chadawa(
    chadawa_id: int = Path(..., ge=1),
    chadawa: ChadawaUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update a chadawa (admin only)"""
    updated_chadawa = chadawas_crud.update_chadawa(db, chadawa_id, chadawa)
    if not updated_chadawa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chadawa not found"
        )
    
    return updated_chadawa

@router.delete("/admin/chadawas/{chadawa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chadawa(
    chadawa_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete a chadawa (admin only)"""
    success = chadawas_crud.delete_chadawa(db, chadawa_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chadawa not found"
        )
    
    return None

@router.post("/admin/pujas/{puja_id}/chadawas/{chadawa_id}", status_code=status.HTTP_200_OK)
def add_chadawa_to_puja(
    puja_id: int = Path(..., ge=1),
    chadawa_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Associate a chadawa with a puja (admin only)"""
    # Check if puja exists
    puja = pujas_crud.get_puja_by_id(db, puja_id)
    if not puja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puja not found"
        )
    
    # Check if chadawa exists
    chadawa = chadawas_crud.get_chadawa_by_id(db, chadawa_id)
    if not chadawa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chadawa not found"
        )
    
    puja_chadawa = chadawas_crud.add_chadawa_to_puja(db, puja_id, chadawa_id)
    return {"message": "Chadawa added to puja successfully"}

@router.delete("/admin/pujas/{puja_id}/chadawas/{chadawa_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_chadawa_from_puja(
    puja_id: int = Path(..., ge=1),
    chadawa_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Remove a chadawa association from a puja (admin only)"""
    success = chadawas_crud.remove_chadawa_from_puja(db, puja_id, chadawa_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chadawa association not found"
        )
    return None
