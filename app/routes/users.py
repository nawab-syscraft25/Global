from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.schemas import UserResponse, UserBase
from app.crud import users as users_crud
from app.auth.auth import get_current_user
from app.models.models import User

router = APIRouter(prefix="/user", tags=["User Profile"])

@router.get("/profile", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    user_data: UserBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user profile"""
    # Update user information
    updated_user = users_crud.update_user(
        db,
        current_user.id,
        user_data.dict(exclude_unset=True)
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user
