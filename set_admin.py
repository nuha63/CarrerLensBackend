import os
import sys
from pathlib import Path
from sqlalchemy import text

# Add the project root to the sys.path
sys.path.append(str(Path(__file__).parent))

from app.database.service import get_db_service

def set_admin(email: str):
    db = get_db_service().get_session()
    try:
        # Update the user profile with the given email using ORM
        from app.database.models import UserProfile
        user = db.query(UserProfile).filter(UserProfile.email == email).first()
        
        if user:
            user.is_admin = True
            db.commit()
            print(f"✅ Successfully set {email} as an admin!")
        else:
            print(f"❌ User with email {email} not found. Make sure the user has signed up first.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python set_admin.py <your_email@example.com>")
    else:
        set_admin(sys.argv[1])
