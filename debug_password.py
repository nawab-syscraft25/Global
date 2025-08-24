#!/usr/bin/env python3
"""
Debug password verification
"""
import sys
import os
from passlib.context import CryptContext

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import app.database
from app.models.models import User

def debug_password():
    # Create database session
    db = app.database.SessionLocal()
    
    try:
        # Get super admin user
        user = db.query(User).filter(User.email == "nawabkh2040@gmail.com").first()
        
        if not user:
            print("❌ User not found")
            return
            
        print(f"✅ User found: {user.email}")
        print(f"   Password hash: {user.password[:50]}...")
        
        # Test with different password contexts
        pwd_context1 = CryptContext(schemes=["bcrypt"], deprecated="auto")
        pwd_context2 = CryptContext(schemes=["bcrypt"])
        
        test_password = "khan@123"
        
        print(f"\nTesting password: '{test_password}'")
        
        # Test verification with different contexts
        result1 = pwd_context1.verify(test_password, user.password)
        result2 = pwd_context2.verify(test_password, user.password)
        
        print(f"   Context 1 (with deprecated='auto'): {result1}")
        print(f"   Context 2 (without deprecated): {result2}")
        
        # Test creating a new hash and verifying
        new_hash = pwd_context1.hash(test_password)
        result3 = pwd_context1.verify(test_password, new_hash)
        
        print(f"   New hash verification: {result3}")
        print(f"   New hash: {new_hash[:50]}...")
        
        # Compare hash formats
        print(f"\nHash comparison:")
        print(f"   Stored hash starts with: {user.password[:10]}")
        print(f"   New hash starts with: {new_hash[:10]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_password()
