import sys
from sqlalchemy import inspect
from app.database import engine

def check_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("Tables in the database:")
    for table in tables:
        print(f"- {table}")
    
    expected_tables = [
        "users", "poojas", "chadawas", "bookings", 
        "payments", "booking_chadawa", "alembic_version"
    ]
    
    missing_tables = [table for table in expected_tables if table not in tables]
    
    if missing_tables:
        print("\nMISSING TABLES:")
        for table in missing_tables:
            print(f"- {table}")
        return False
    else:
        print("\nAll expected tables exist!")
        return True

if __name__ == "__main__":
    success = check_tables()
    sys.exit(0 if success else 1)
