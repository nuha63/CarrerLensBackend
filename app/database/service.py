"""
Database Service - Handle CRUD operations for all models
"""
import logging
from typing import Optional, List
import uuid
from datetime import datetime, date, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os

from app.database.models import (
    Base, UserProfile, UserResume, ResumeAnalysis, 
    JobMatch, SkillGap, SalaryPrediction, UserProgress
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseService:
    def __init__(self):
        """Initialize database connection"""
        # Get database URL from environment
        database_url = os.getenv(
            "DATABASE_URL",
            "sqlite:///./carrer_lens.db"  # Fallback to SQLite for local dev
        )
        
        # Convert async PostgreSQL URL to sync for SQLAlchemy
        if "postgresql+asyncpg" in database_url:
            database_url = database_url.replace("postgresql+asyncpg", "postgresql")
        
        # Strip unsupported query parameters that psycopg2 doesn't understand
        # (e.g. channel_binding=require from Neon connection strings)
        if "?" in database_url:
            base, params = database_url.split("?", 1)
            filtered = "&".join(
                p for p in params.split("&")
                if not p.startswith("channel_binding")
            )
            database_url = f"{base}?{filtered}" if filtered else base
        
        logger.info(f"Database URL: {database_url[:50]}...")
        
        # Create engine
        if "sqlite" in database_url:
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            self.engine = create_engine(
                database_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=1800,  # Recycle connections every 30 minutes
            )
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        logger.info("✅ Database tables created/verified")
        
        # Create session factory
        # expire_on_commit=False keeps attributes accessible after session.close()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine, expire_on_commit=False)
        
        # Initialize default features
        self._init_features()
    
    def _init_features(self):
        """Initialize default system features if they don't exist"""
        db = self.get_session()
        try:
            from app.database.models import SystemFeature
            default_features = [
                {"id": "resume_analysis", "name": "Resume Analysis", "description": "AI-powered resume parsing and scoring"},
                {"id": "job_matching", "name": "Job Matching", "description": "Match resumes to job descriptions"},
                {"id": "salary_prediction", "name": "Salary Prediction", "description": "Predict salary based on skills"},
                {"id": "roadmaps", "name": "Career Roadmaps", "description": "Generate step-by-step career roadmaps"},
                {"id": "skill_gap", "name": "Skill Gap Analysis", "description": "Analyze missing skills for target roles"},
            ]
            for feat in default_features:
                existing = db.query(SystemFeature).filter(SystemFeature.id == feat["id"]).first()
                if not existing:
                    db.add(SystemFeature(**feat))
            db.commit()
        except Exception as e:
            logger.error(f"Error initializing features: {e}")
        finally:
            db.close()

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    # ==================== User Profile ====================
    
    def create_user(self, email: str, name: str = "", **kwargs) -> UserProfile:
        """Create or update user profile"""
        db = self.get_session()
        try:
            # Check if user exists
            user = db.query(UserProfile).filter(UserProfile.email == email).first()
            if user:
                logger.info(f"User {email} already exists, updating")
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
            else:
                user = UserProfile(email=email, name=name, **kwargs)
                db.add(user)

            db.commit()
            # Refresh BEFORE closing so all columns are loaded into the instance.
            # With expire_on_commit=False this is a safety net; required without it.
            db.refresh(user)
            logger.info(f"✅ User created/updated: {email}")
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error creating user: {e}")
            raise
        finally:
            db.close()
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Get user by ID"""
        db = self.get_session()
        try:
            user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            return user
        finally:
            db.close()
    
    # ==================== Resume ====================
    
    def save_resume(self, user_id: str, file_name: str, resume_text: str,
                   skills_found: Optional[List[str]] = None, **kwargs) -> UserResume:
        """Save uploaded resume"""
        db = self.get_session()
        try:
            resume = UserResume(
                user_id=user_id,
                file_name=file_name,
                resume_text=resume_text,
                skills_found=skills_found or [],
                **kwargs
            )
            db.add(resume)
            db.commit()
            db.refresh(resume)  # load all columns before session closes
            logger.info(f"✅ Resume saved: {file_name}")
            return resume
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error saving resume: {e}")
            raise
        finally:
            db.close()
    
    def get_user_resumes(self, user_id: str) -> List[UserResume]:
        """Get all resumes for user"""
        db = self.get_session()
        try:
            resumes = db.query(UserResume).filter(UserResume.user_id == user_id).all()
            return resumes
        finally:
            db.close()
    
    # ==================== Resume Analysis ====================
    
    def save_resume_analysis(self, user_id: str, analysis_data: dict) -> ResumeAnalysis:
        """Save resume analysis results"""
        db = self.get_session()
        try:
            analysis = ResumeAnalysis(user_id=user_id, **analysis_data)
            db.add(analysis)
            db.commit()
            db.refresh(analysis)  # load all columns before session closes
            logger.info(f"✅ Resume analysis saved: {analysis.analysis_id}")
            return analysis
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error saving analysis: {e}")
            raise
        finally:
            db.close()
    
    def get_user_analyses(self, user_id: str, limit: int = 10) -> List[ResumeAnalysis]:
        """Get recent analyses for user"""
        db = self.get_session()
        try:
            analyses = db.query(ResumeAnalysis)\
                .filter(ResumeAnalysis.user_id == user_id)\
                .order_by(ResumeAnalysis.created_at.desc())\
                .limit(limit).all()
            return analyses
        finally:
            db.close()
    
    # ==================== Job Match ====================
    
    def save_job_match(self, user_id: str, analysis_id: str, match_data: dict) -> JobMatch:
        """Save job matching prediction"""
        db = self.get_session()
        try:
            job_match = JobMatch(user_id=user_id, analysis_id=analysis_id, **match_data)
            db.add(job_match)
            db.commit()
            logger.info(f"✅ Job match saved: {job_match.match_id}")
            return job_match
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error saving job match: {e}")
            raise
        finally:
            db.close()
    
    def get_user_matches(self, user_id: str, limit: int = 20) -> List[JobMatch]:
        """Get job matches for user"""
        db = self.get_session()
        try:
            matches = db.query(JobMatch)\
                .filter(JobMatch.user_id == user_id)\
                .order_by(JobMatch.match_score.desc())\
                .limit(limit).all()
            return matches
        finally:
            db.close()
    
    # ==================== Skill Gap ====================
    
    def save_skill_gap(self, user_id: str, match_id: str, gap_data: dict) -> SkillGap:
        """Save skill gap analysis"""
        db = self.get_session()
        try:
            skill_gap = SkillGap(user_id=user_id, match_id=match_id, **gap_data)
            db.add(skill_gap)
            db.commit()
            logger.info(f"✅ Skill gap saved: {skill_gap.gap_id}")
            return skill_gap
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error saving skill gap: {e}")
            raise
        finally:
            db.close()
    
    def get_user_skill_gaps(self, user_id: str, limit: int = 10) -> List[SkillGap]:
        """Get skill gaps for user"""
        db = self.get_session()
        try:
            gaps = db.query(SkillGap)\
                .filter(SkillGap.user_id == user_id)\
                .order_by(SkillGap.created_at.desc())\
                .limit(limit).all()
            return gaps
        finally:
            db.close()
    
    # ==================== Salary Prediction ====================
    
    def save_salary_prediction(self, user_id: str, match_id: str, 
                              salary_data: dict) -> SalaryPrediction:
        """Save salary prediction"""
        db = self.get_session()
        try:
            prediction = SalaryPrediction(user_id=user_id, match_id=match_id, **salary_data)
            db.add(prediction)
            db.commit()
            logger.info(f"✅ Salary prediction saved: {prediction.prediction_id}")
            return prediction
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error saving salary prediction: {e}")
            raise
        finally:
            db.close()
    
    # ==================== User Progress ====================
    
    def get_or_create_progress(self, user_id: str) -> UserProgress:
        """Get or create user progress"""
        db = self.get_session()
        try:
            progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
            if not progress:
                progress = UserProgress(user_id=user_id)
                db.add(progress)
                db.commit()
                logger.info(f"✅ Progress created for user: {user_id}")
            return progress
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error getting progress: {e}")
            raise
        finally:
            db.close()
    
    def update_progress(self, user_id: str, **kwargs) -> UserProgress:
        """Update user progress"""
        db = self.get_session()
        try:
            progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
            if not progress:
                progress = UserProgress(user_id=user_id)
            
            for key, value in kwargs.items():
                if hasattr(progress, key):
                    setattr(progress, key, value)
            
            setattr(progress, 'updated_at', datetime.now(timezone.utc))
            setattr(progress, 'last_activity', datetime.now(timezone.utc))
            
            db.add(progress)
            db.commit()
            logger.info(f"✅ Progress updated for user: {user_id}")
            return progress
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error updating progress: {e}")
            raise
        finally:
            db.close()


# Singleton instance
_db_service_instance = None


def get_db_service() -> DatabaseService:
    """Get or create database service singleton"""
    global _db_service_instance
    if _db_service_instance is None:
        _db_service_instance = DatabaseService()
    return _db_service_instance
