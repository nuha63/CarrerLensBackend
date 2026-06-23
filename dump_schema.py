import os
import sys
from sqlalchemy import create_engine, inspect

from dotenv import load_dotenv
load_dotenv('.env')

url = os.getenv('DATABASE_URL')
if 'postgresql+asyncpg' in url:
    url = url.replace('postgresql+asyncpg', 'postgresql')

engine = create_engine(url)
insp = inspect(engine)

for table in ['career_paths', 'roadmap_phases', 'roadmap_skills', 'user_skill_progress']:
    try:
        columns = insp.get_columns(table)
        print(f'Table: {table}')
        for c in columns:
            print(f'  {c["name"]}: {c["type"]}')
        print('')
    except Exception as e:
        print(f'Error getting table {table}: {e}')
