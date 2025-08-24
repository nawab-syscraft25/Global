#!/usr/bin/env python3
"""
Fix super admin role to match enum
"""
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import app.database
from app.models.models import User

def fix_super_admin_role():
    # Create database session
    db = app.database.SessionLocal()
    
    try:
        # Find super admin user
        super_admin = db.query(User).filter(User.email == "nawabkh2040@gmail.com").first()
        
        if not super_admin:
            print("❌ Super admin user not found!")
            return
        
        print(f"Current role: {super_admin.role}")
        
        # Update role to match enum
        if super_admin.role == "super_admin":
            super_admin.role = "super_admin"
            db.commit()
            print(f"✅ Updated role to: {super_admin.role}")
        else:
            print(f"✅ Role is already correct: {super_admin.role}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_super_admin_role()
