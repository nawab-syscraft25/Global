from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.schemas import PujaResponse, PujaCreate, PujaUpdate, PujaWithDetails
from app.schemas.schemas import PujaImageCreate, PujaImage, PlanCreate, PlanResponse
from app.crud import pujas as pujas_crud
from app.auth.auth import get_current_user, get_admin_user
from app.models.models import User

router = APIRouter(tags=["Pujas"])

# Public routes
@router.get("/pujas", response_model=List[PujaResponse])
def get_pujas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of all pujas"""
    return pujas_crud.get_pujas(db, skip, limit)

@router.get("/pujas/details", response_model=List[PujaWithDetails])
def get_pujas_with_details(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of all pujas with details including images, plans, and chadawas"""
    return pujas_crud.get_pujas_with_details(db, skip, limit)

@router.get("/pujas/{puja_id}", response_model=PujaWithDetails)
def get_puja(puja_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    """Get a specific puja by ID with all details"""
    puja = pujas_crud.get_puja_by_id(db, puja_id)
    if not puja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puja not found"
        )
    return puja

# Plans
@router.get("/plans", response_model=List[PlanResponse])
def get_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of all plans"""
    return pujas_crud.get_plans(db, skip, limit)

@router.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    """Get a specific plan by ID"""
    plan = pujas_crud.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan

# Admin routes - Pujas
@router.post("/admin/pujas", response_model=PujaResponse, status_code=status.HTTP_201_CREATED)
def create_puja(
    puja: PujaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new puja (admin only)"""
    return pujas_crud.create_puja(db, puja)

@router.put("/admin/pujas/{puja_id}", response_model=PujaResponse)
def update_puja(
    puja_id: int = Path(..., ge=1),
    puja: PujaUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update a puja (admin only)"""
    updated_puja = pujas_crud.update_puja(db, puja_id, puja)
    if not updated_puja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puja not found"
        )
    return updated_puja

@router.delete("/admin/pujas/{puja_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_puja(
    puja_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete a puja (admin only)"""
    success = pujas_crud.delete_puja(db, puja_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puja not found"
        )
    return None

# Admin routes - Puja Images
@router.post("/admin/pujas/images", response_model=PujaImage, status_code=status.HTTP_201_CREATED)
def add_puja_image(
    image: PujaImageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Add an image to a puja (admin only)"""
    # First check if the puja exists
    puja = pujas_crud.get_puja_by_id(db, image.puja_id)
    if not puja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puja not found"
        )
    return pujas_crud.add_puja_image(db, image)

@router.delete("/admin/pujas/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_puja_image(
    image_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete a puja image (admin only)"""
    success = pujas_crud.delete_puja_image(db, image_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puja image not found"
        )
    return None

# Admin routes - Plans
@router.post("/admin/plans", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    plan: PlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new plan (admin only)"""
    return pujas_crud.create_plan(db, plan)

# Associate plans with pujas
@router.post("/admin/pujas/{puja_id}/plans/{plan_id}", status_code=status.HTTP_200_OK)
def add_plan_to_puja(
    puja_id: int = Path(..., ge=1),
    plan_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Associate a plan with a puja (admin only)"""
    # Check if puja exists
    puja = pujas_crud.get_puja_by_id(db, puja_id)
    if not puja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puja not found"
        )
    
    # Check if plan exists
    plan = pujas_crud.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    puja_plan = pujas_crud.add_plan_to_puja(db, puja_id, plan_id)
    return {"message": "Plan added to puja successfully"}

@router.delete("/admin/pujas/{puja_id}/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_plan_from_puja(
    puja_id: int = Path(..., ge=1),
    plan_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Remove a plan association from a puja (admin only)"""
    success = pujas_crud.remove_plan_from_puja(db, puja_id, plan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan association not found"
        )
    return None
