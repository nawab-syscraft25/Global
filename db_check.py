import sys
from app.database import engine
from app.config import settings

def check_db_connection():
    try:
        # Try to connect to the database
        conn = engine.connect()
        conn.close()
        print("Database connection successful!")
        print(f"Connected to: {settings.DATABASE_URL}")
        return True
    except Exception as e:
        print(f"Error connecting to the database: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_db_connection()
    sys.exit(0 if success else 1)
