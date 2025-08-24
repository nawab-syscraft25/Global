#!/usr/bin/env python3
"""
Test FastAPI OAuth2PasswordRequestForm behavior
"""
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import app.database
from app.auth.auth import authenticate_user_with_password

def test_fastapi_auth():
    # Create database session
    db = app.database.SessionLocal()
    
    try:
        # Test the exact same function that FastAPI calls
        email = "nawabkh2040@gmail.com"
        password = "khan@123"
        
        print(f"Testing authenticate_user_with_password:")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"  Password repr: {repr(password)}")
        
        result = authenticate_user_with_password(db, email, password)
        
        if result:
            print(f"✅ Authentication successful!")
            print(f"   User ID: {result.id}")
            print(f"   Role: {result.role}")
        else:
            print(f"❌ Authentication failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_fastapi_auth()
