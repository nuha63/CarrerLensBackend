import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

url = os.environ["DATABASE_URL"]
url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://")

engine = create_engine(url)

with engine.begin() as conn:
    print("Altering user_progress table...")
    try:
        conn.execute(text("ALTER TABLE user_progress ADD COLUMN study_hours_logged FLOAT DEFAULT 0.0;"))
        conn.execute(text("ALTER TABLE user_progress ADD COLUMN last_study_date DATE;"))
        print("Columns added successfully!")
    except Exception as e:
        print(f"Error (maybe columns already exist?): {e}")
