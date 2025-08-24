#!/usr/bin/env python3
"""
Script to create a super admin user
"""
import sys
import os
from datetime import datetime
from passlib.context import CryptContext

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Import the SessionLocal from database.py
import app.database
from app.models.models import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_super_admin():
    # Create database session
    db = app.database.SessionLocal()
    
    try:
        # Check if super admin already exists
        existing_admin = db.query(User).filter(User.email == "nawabkh2040@gmail.com").first()
        
        if existing_admin:
            print("Super admin user already exists!")
            print(f"Email: {existing_admin.email}")
            print(f"Role: {existing_admin.role}")
            print(f"Active: {existing_admin.is_active}")
            return
        
        # Hash the password
        hashed_password = hash_password("khan@123")
        
        # Create super admin user
        super_admin = User(
            name="Nawab khan",
            email="nawabkh2040@gmail.com",
            mobile="8962507486",  # You can change this
            role="super_admin",
            password=hashed_password,
            is_active=True,  # Super admin is active by default
            email_verified=True,  # Set as verified
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(super_admin)
        db.commit()
        
        print("Super admin user created successfully!")
        print(f"Email: {super_admin.email}")
        print(f"Role: {super_admin.role}")
        print(f"Active: {super_admin.is_active}")
        print(f"Email Verified: {super_admin.email_verified}")
        
    except Exception as e:
        print(f"Error creating super admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_super_admin()
