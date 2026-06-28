import os
import sys
from pathlib import Path
from sqlalchemy import text

# Add the project root to the sys.path
sys.path.append(str(Path(__file__).parent))

from app.database.service import get_db_service
from app.database.models import Base

def alter_db():
    db = get_db_service().get_session()
    engine = get_db_service().engine
    
    alters = [
        "ALTER TABLE user_profiles ADD COLUMN is_premium BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE user_profiles ADD COLUMN premium_expiry TIMESTAMP;",
        "ALTER TABLE user_profiles ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;"
    ]
    
    # Try running alters
    for query in alters:
        try:
            db.execute(text(query))
            db.commit()
            print(f"✅ Executed: {query}")
        except Exception as e:
            db.rollback()
            print(f"ℹ️ Skipped (might already exist or SQLite syntax issue): {query} - Error: {e}")
            
    # Create any missing tables (e.g., the new payments table)
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Created new tables (e.g., payments) if they didn't exist.")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
            
    db.close()
    print("Database modification finished.")

if __name__ == "__main__":
    alter_db()
