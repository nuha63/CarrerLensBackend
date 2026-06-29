import os
import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Grab DB URL from .env since we're running locally
from dotenv import load_dotenv
load_dotenv()

database_url = os.getenv("DATABASE_URL")
print(f"Original DB URL: {database_url}")

# 2. Simulate what service.py does
if "postgresql+asyncpg" in database_url:
    database_url = database_url.replace("postgresql+asyncpg", "postgresql")

if "?" in database_url:
    base, params = database_url.split("?", 1)
    filtered = "&".join(
        p for p in params.split("&")
        if not p.startswith("channel_binding")
    )
    database_url = f"{base}?{filtered}" if filtered else base

print(f"Processed DB URL: {database_url}")

# 3. Try to connect and run a query
try:
    engine = create_engine(database_url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Try a simple execute
    from sqlalchemy import text
    result = db.execute(text("SELECT 1")).scalar()
    print(f"✅ DB Connection successful! Result: {result}")
    
    # Try querying UserProfile to see if the table exists
    from app.database.models import UserProfile
    users = db.query(UserProfile).limit(1).all()
    print(f"✅ UserProfile query successful! Found {len(users)} users.")
    
except Exception as e:
    print(f"❌ DB Error: {type(e).__name__}: {e}")
    traceback.print_exc()
finally:
    try:
        db.close()
    except:
        pass
