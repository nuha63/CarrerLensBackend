import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

url = os.environ["DATABASE_URL"]
url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://")

engine = create_engine(url)

with engine.begin() as conn:
    print("Altering user_skill_progress table...")
    try:
        conn.execute(text("ALTER TABLE user_skill_progress ALTER COLUMN user_id TYPE VARCHAR;"))
        print("Column type altered successfully!")
    except Exception as e:
        print(f"Error: {e}")
