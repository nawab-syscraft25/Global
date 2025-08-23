import os
import urllib.parse
from sqlalchemy import create_engine, text

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:nNAWAB%4064293975@db.wtycdayayaewgrsputpm.supabase.co:5432/postgres")

def check_users():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Check user count
            result = conn.execute(text('SELECT COUNT(*) FROM users'))
            count = result.fetchone()[0]
            print(f'Total users in database: {count}')
            
            if count > 0:
                # Check sample users
                result = conn.execute(text('SELECT id, name, email, phone FROM users LIMIT 5'))
                rows = result.fetchall()
                print('\nSample users:')
                for row in rows:
                    print(f'  ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Phone: {row[3]}')
                    
                # Check if any users have null phones (which would become mobile)
                result = conn.execute(text('SELECT COUNT(*) FROM users WHERE phone IS NULL'))
                null_phones = result.fetchone()[0]
                print(f'\nUsers with NULL phone: {null_phones}')
                
            else:
                print("No users found in database - migration should be safe")
                
    except Exception as e:
        print(f"Error checking users: {e}")

if __name__ == "__main__":
    check_users()
