import asyncio
from app.database.service import get_db_service
from app.database.models import CareerPath

async def main():
    db_service = get_db_service()
    session = db_service.get_session()
    
    paths = session.query(CareerPath).all()
    for path in paths:
        print(f"ID: {path.id}, Name: {path.name}, Phases: {len(path.phases)}")
        
if __name__ == "__main__":
    asyncio.run(main())
