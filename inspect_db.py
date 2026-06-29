import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

url = os.environ["DATABASE_URL"]
url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://")

engine = create_engine(url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user_skill_progress';"))
    for row in result:
        print(row)
