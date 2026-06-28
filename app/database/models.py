"""
Database Models - SQLAlchemy ORM models for data persistence
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Date, JSON, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

Base = declarative_base()


class UserProfile(Base):
    """User profile model"""
    __tablename__ = "user_profiles"
    
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    name = Column(String)
    experience_years = Column(Integer, default=0)
    education_level = Column(String, default="Bachelor")  # High School, Bachelor, Master, PhD
    current_industry = Column(String, default="IT")
    target_skills = Column(JSON, default=[])
    profile_image_url = Column(String, nullable=True)
    is_premium = Column(Boolean, default=False)
    premium_expiry = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<UserProfile(email={self.email}, name={self.name})>"


class UserResume(Base):
    """Store uploaded resumes"""
    __tablename__ = "user_resumes"
    
    resume_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    file_name = Column(String)
    file_path = Column(String)
    resume_text = Column(Text)  # Extracted text from PDF/DOCX
    skills_found = Column(JSON, default=[])
    experience_years = Column(Integer)
    education_level = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<UserResume(user_id={self.user_id}, file={self.file_name})>"


class ResumeAnalysis(Base):
    """Store resume analysis results"""
    __tablename__ = "resume_analyses"
    
    analysis_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    resume_id = Column(String, index=True)
    
    # Input features
    experience_years = Column(Integer)
    education_level = Column(String)
    skills_match_score = Column(Float)
    location_type = Column(String, default="Remote")
    industry = Column(String)
    job_market_demand = Column(String)
    
    # Prediction results
    resume_score = Column(Float)  # 0-1
    match_percentage = Column(Integer)  # 0-100
    strengths = Column(JSON, default=[])
    weaknesses = Column(JSON, default=[])
    suggestions = Column(JSON, default=[])
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<ResumeAnalysis(user_id={self.user_id}, score={self.resume_score})>"


class JobMatch(Base):
    """Store job matching predictions"""
    __tablename__ = "job_matches"
    
    match_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    analysis_id = Column(String, index=True)
    
    # Job info
    job_title = Column(String)
    company = Column(String, default="Unknown")
    industry = Column(String)
    salary_range = Column(String)
    required_skills = Column(JSON, default=[])
    
    # Prediction results
    match_score = Column(Float)  # 0-1
    interview_probability = Column(Float)  # 0-1
    recommendation = Column(String)  # Strong/Moderate/Weak
    confidence = Column(Float)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<JobMatch(user_id={self.user_id}, job={self.job_title}, match={self.match_score})>"


class SkillGap(Base):
    """Store skill gap analysis"""
    __tablename__ = "skill_gaps"
    
    gap_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    match_id = Column(String, index=True)
    
    # Input
    user_skills = Column(JSON, default=[])
    target_job = Column(String)
    
    # Analysis results
    missing_skills = Column(JSON, default=[])
    priority_skills = Column(JSON, default=[])  # Top 10 most important
    total_missing = Column(Integer, default=0)
    skill_demands = Column(JSON, default={})  # skill -> demand score
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<SkillGap(user_id={self.user_id}, target_job={self.target_job}, missing={self.total_missing})>"


class SalaryPrediction(Base):
    """Store salary predictions"""
    __tablename__ = "salary_predictions"
    
    prediction_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    match_id = Column(String, index=True)
    
    # Input
    job_role = Column(String)
    experience_years = Column(Integer)
    education_level = Column(String)
    num_skills = Column(Integer)
    high_demand_skills = Column(JSON, default=[])
    
    # Results
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_avg = Column(Integer)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<SalaryPrediction(user_id={self.user_id}, avg=${self.salary_avg})>"

class SalaryBenchmark(Base):
    """Bangladesh market salary benchmarks"""
    __tablename__ = "salary_benchmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    job_role = Column(String, nullable=False, index=True)
    experience_level = Column(String, nullable=False) # Fresher, Mid, Senior
    min_salary = Column(Integer, nullable=False)
    max_salary = Column(Integer, nullable=False)
    avg_salary = Column(Integer, nullable=False)
    
    def __repr__(self):
        return f"<SalaryBenchmark(role={self.job_role}, level={self.experience_level})>"


class UserProgress(Base):
    """Track user learning progress"""
    __tablename__ = "user_progress"
    
    progress_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    
    # Progress metrics
    resumes_analyzed = Column(Integer, default=0)
    jobs_matched = Column(Integer, default=0)
    skills_learned = Column(JSON, default=[])
    skills_in_progress = Column(JSON, default=[])
    job_readiness_score = Column(Float, default=0.0)  # 0-100
    
    # Learning goals
    target_skills = Column(JSON, default=[])
    preferred_job_categories = Column(JSON, default=[])  # New dedicated column
    daily_study_hours_goal = Column(Integer, default=1)
    learning_pace = Column(String, default="medium")  # slow, medium, fast
    
    # Daily Tracking
    study_hours_logged = Column(Float, default=0.0)
    last_study_date = Column(Date, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, readiness={self.job_readiness_score})>"


class CareerPath(Base):
    """Maps to the existing career_paths table in Neon DB"""
    __tablename__ = "career_paths"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)

    phases = relationship(
        "RoadmapPhase",
        back_populates="career_path",
        order_by="RoadmapPhase.phase_order"
    )

    def __repr__(self):
        return f"<CareerPath(id={self.id}, name={self.name})>"


class RoadmapPhase(Base):
    __tablename__ = "roadmap_phases"

    id = Column(Integer, primary_key=True, index=True)

    career_id = Column(
        Integer,
        ForeignKey("career_paths.id"),
        nullable=False
    )

    phase_order = Column(Integer)
    phase_name = Column(String)

    career_path = relationship(
        "CareerPath",
        back_populates="phases"
    )

    skills = relationship(
        "RoadmapSkill",
        back_populates="phase",
        order_by="RoadmapSkill.skill_order"
    )


class RoadmapSkill(Base):
    __tablename__ = "roadmap_skills"

    id = Column(Integer, primary_key=True, index=True)

    phase_id = Column(
        Integer,
        ForeignKey("roadmap_phases.id"),
        nullable=False
    )

    skill_order = Column(Integer)
    skill_name = Column(String)

    phase = relationship(
        "RoadmapPhase",
        back_populates="skills"
    )


class UserSkillProgress(Base):
    """Maps to the existing user_skill_progress table in Neon DB"""
    __tablename__ = "user_skill_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    skill_id = Column(Integer, ForeignKey("roadmap_skills.id"), nullable=False, index=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<UserSkillProgress(user_id={self.user_id}, skill_id={self.skill_id}, completed={self.is_completed})>"

class Payment(Base):
    """Store payment and premium requests"""
    __tablename__ = "payments"
    
    payment_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, approved, rejected
    payment_method = Column(String)  # bKash, Card, etc.
    transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Payment(user_id={self.user_id}, amount={self.amount}, status={self.status})>"

