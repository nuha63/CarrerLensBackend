import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.database.service import get_db_service
from app.database.models import UserProfile

def make_admin(email):
    db_service = get_db_service()
    db = db_service.get_session()
    try:
        user = db.query(UserProfile).filter(UserProfile.email == email).first()
        if user:
            user.is_admin = True
            db.commit()
            print(f"✅ Success! {email} is now an Admin in the database.")
        else:
            print(f"❌ User {email} not found in database. Try signing up in the app first, then run this script.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    make_admin("sanjidaislamnimu@gmail.com")
