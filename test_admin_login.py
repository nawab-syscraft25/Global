#!/usr/bin/env python3
"""
Script to test admin login and verify super admin user
"""
import sys
import os
from passlib.context import CryptContext

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Import the SessionLocal from database.py
import app.database
from app.models.models import User
from app.auth.auth import authenticate_user_with_password

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_admin_login():
    # Create database session
    db = app.database.SessionLocal()
    
    try:
        # Check if super admin exists
        super_admin = db.query(User).filter(User.email == "nawabkh2040@gmail.com").first()
        
        if not super_admin:
            print("❌ Super admin user not found!")
            return
        
        print("✅ Super admin user found:")
        print(f"   ID: {super_admin.id}")
        print(f"   Name: {super_admin.name}")
        print(f"   Email: {super_admin.email}")
        print(f"   Mobile: {super_admin.mobile}")
        print(f"   Role: {super_admin.role}")
        print(f"   Active: {super_admin.is_active}")
        print(f"   Email Verified: {super_admin.email_verified}")
        print(f"   Has Password: {'Yes' if super_admin.password else 'No'}")
        
        # Test password verification
        if super_admin.password:
            password_check = pwd_context.verify("khan@123", super_admin.password)
            print(f"   Password Check: {'✅ Valid' if password_check else '❌ Invalid'}")
            
            # Test authentication function
            auth_result = authenticate_user_with_password(db, "nawabkh2040@gmail.com", "khan@123")
            print(f"   Auth Function: {'✅ Success' if auth_result else '❌ Failed'}")
        else:
            print("   ❌ No password set for super admin!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_admin_login()
