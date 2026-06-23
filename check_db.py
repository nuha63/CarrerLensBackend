import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

url = os.environ["DATABASE_URL"]
url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://")

engine = create_engine(url)

with engine.begin() as conn:
    print("Dropping tables...")
    conn.execute(text("DROP TABLE IF EXISTS salary_predictions CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS skill_gaps CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS job_matches CASCADE;"))
    print("Tables dropped!")