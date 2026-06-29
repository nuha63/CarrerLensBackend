from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)

DATABASE_URL = "postgresql://neondb_owner:npg_SUEfLdeJ1a9j@ep-red-sound-anp7w9yc-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_set_phase_completion():
    db = SessionLocal()
    try:
        from app.database.models import RoadmapPhase, UserSkillProgress
        from datetime import datetime, timezone
        
        user_id = "test_user"
        is_completed = True
        
        phase = db.query(RoadmapPhase).filter(RoadmapPhase.phase_name == "Projects & System Design").first()
        if not phase:
            print("Phase not found by name")
            return
            
        print(f"Found Phase ID: {phase.id}")
        
        for skill in phase.skills:
            print(f"Processing skill: {skill.skill_name} (ID: {skill.id})")
            record = db.query(UserSkillProgress).filter(
                UserSkillProgress.user_id == user_id,
                UserSkillProgress.skill_id == skill.id
            ).first()

            if not record:
                print(f"Creating new record for skill_id: {skill.id}")
                record = UserSkillProgress(
                    user_id=user_id,
                    skill_id=skill.id,
                )
                db.add(record)

            record.is_completed = is_completed
            record.completed_at = datetime.now(timezone.utc) if is_completed else None

        db.commit()
        print("Success")
    except Exception as e:
        print(f"Exception: {e}")
        db.rollback()
    finally:
        db.close()

test_set_phase_completion()
