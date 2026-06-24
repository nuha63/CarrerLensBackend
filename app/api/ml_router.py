"""
ML API Router - ML predictions with database persistence
"""
from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.services.ml_service import get_ml_service
from app.database.service import get_db_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ML Analysis"])


# ============ Request/Response Models ============

class ResumeAnalysisRequest(BaseModel):
    experience_years: int
    education_level: str  # "High School", "Bachelor", "Master", "PhD"
    skills_match_score: float  # 0-100
    location_type: Optional[str] = "Remote"
    industry: Optional[str] = "IT"
    job_market_demand: Optional[str] = "High"


class PreferencesRequest(BaseModel):
    target_skills: Optional[List[str]] = None
    daily_study_hours_goal: Optional[int] = None
    learning_pace: Optional[str] = None
    preferred_categories: Optional[List[str]] = None


class LogHoursRequest(BaseModel):
    hours: float


class CompleteSkillRequest(BaseModel):
    skill: str


class JobMatchRequest(BaseModel):
    job_title: str
    company: Optional[str] = "Unknown"
    industry: str
    resume_score: float  # 0-1
    skills_match_score: float  # 0-100
    experience_years: int
    education_level: str
    job_market_demand: Optional[str] = "High"
    required_skills: Optional[List[str]] = None


class SalaryPredictionRequest(BaseModel):
    job_role: str
    experience_years: int
    education_level: str
    num_skills: int
    high_demand_skills: List[str]


class SkillGapRequest(BaseModel):
    user_skills: List[str]
    target_job: str


# ============ API Endpoints ============

@router.post("/analyze-resume")
async def analyze_resume(request: ResumeAnalysisRequest, x_user_id: Optional[str] = Header(None)):
    """
    Analyze resume quality and save to database
    
    Pass user_id via X-User-ID header to save to database
    """
    try:
        ml_service = get_ml_service()
        
        # Get ML prediction
        result = ml_service.analyze_resume(
            experience_years=request.experience_years,
            education_level=request.education_level,
            skills_match_score=request.skills_match_score,
            location_type=request.location_type or "Remote",
            industry=request.industry or "IT",
            job_market_demand=request.job_market_demand or "High"
        )
        
        # Save to database if user_id provided
        if x_user_id:
            db_service = get_db_service()
            analysis_data = {
                "experience_years": request.experience_years,
                "education_level": request.education_level,
                "skills_match_score": request.skills_match_score,
                "location_type": request.location_type,
                "industry": request.industry,
                "job_market_demand": request.job_market_demand,
                "resume_score": result['resume_score'],
                "match_percentage": result['match_percentage'],
                "strengths": result['strengths'],
                "weaknesses": result['weaknesses'],
                "suggestions": result['suggestions'],
            }
            db_service.save_resume_analysis(x_user_id, analysis_data)
            logger.info(f"✅ Resume analyzed & saved for user: {x_user_id}")
        else:
            logger.info("⚠️  No user_id provided, skipping database save")
        
        logger.info(f"✅ Resume analyzed: score={result['match_percentage']}%")
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"❌ Resume analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/job-match")
async def match_job(request: JobMatchRequest, x_user_id: Optional[str] = Header(None)):
    """
    Predict job match probability and save to database
    
    Pass user_id via X-User-ID header to save to database
    """
    try:
        ml_service = get_ml_service()
        
        # Get ML prediction
        result = ml_service.match_job(
            resume_score=request.resume_score,
            skills_match_score=request.skills_match_score,
            experience_years=request.experience_years,
            education_level=request.education_level,
            industry=request.industry or "IT",
            job_market_demand=request.job_market_demand or "High"
        )
        
        # Save to database if user_id provided
        if x_user_id:
            db_service = get_db_service()
            match_data = {
                "job_title": request.job_title,
                "company": request.company,
                "industry": request.industry,
                "required_skills": request.required_skills or [],
                "match_score": result['match_score'],
                "interview_probability": result['interview_probability'],
                "recommendation": result['recommendation'],
                "confidence": result['confidence'],
            }
            job_match = db_service.save_job_match(x_user_id, "", match_data)
            logger.info(f"✅ Job match analyzed & saved for user: {x_user_id}")
        
        logger.info(f"✅ Job match analyzed: probability={result['interview_probability']:.2%}")
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"❌ Job match error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/skill-gap")
async def analyze_skill_gap(request: SkillGapRequest, x_user_id: Optional[str] = Header(None)):
    """
    Analyze skill gaps and save to database
    
    Pass user_id via X-User-ID header to save to database
    """
    try:
        ml_service = get_ml_service()
        result = ml_service.analyze_skill_gaps(
            user_skills=request.user_skills,
            target_job=request.target_job
        )
        
        # Save to database if user_id provided
        if x_user_id:
            db_service = get_db_service()
            gap_data = {
                "user_skills": request.user_skills,
                "target_job": request.target_job,
                "missing_skills": result['missing_skills'],
                "priority_skills": result['priority_skills'],
                "total_missing": result['total_missing'],
                "skill_demands": result['skill_demands'],
            }
            db_service.save_skill_gap(x_user_id, "", gap_data)
            logger.info(f"✅ Skill gap analyzed & saved for user: {x_user_id}")
        
        logger.info(f"✅ Skill gap analyzed: {result['total_missing']} missing skills")
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"❌ Skill gap analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/salary-prediction")
async def predict_salary(request: SalaryPredictionRequest, x_user_id: Optional[str] = Header(None)):
    """
    Predict salary range and save to database
    
    Pass user_id via X-User-ID header to save to database
    """
    try:
        ml_service = get_ml_service()
        result = ml_service.predict_salary(
            job_role=request.job_role,
            experience_years=request.experience_years,
            education_level=request.education_level,
            num_skills=request.num_skills,
            high_demand_skills=request.high_demand_skills
        )
        
        # Save to database if user_id provided
        if x_user_id:
            db_service = get_db_service()
            salary_data = {
                "job_role": request.job_role,
                "experience_years": request.experience_years,
                "education_level": request.education_level,
                "num_skills": request.num_skills,
                "high_demand_skills": request.high_demand_skills,
                "salary_min": result['salary_min'],
                "salary_max": result['salary_max'],
                "salary_avg": result['salary_avg'],
            }
            db_service.save_salary_prediction(x_user_id, "", salary_data)
            logger.info(f"✅ Salary predicted & saved for user: {x_user_id}")
        
        logger.info(f"✅ Salary predicted: {result['salary_avg']} BDT")
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"❌ Salary prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ml-status")
async def ml_status():
    """Check if ML models and database are ready"""
    try:
        ml_service = get_ml_service()
        db_service = get_db_service()
        
        models_ready = (
            ml_service.resume_scorer is not None and
            ml_service.job_matcher is not None and
            ml_service.salary_predictor is not None and
            ml_service.skill_gap_analyzer is not None
        )
        
        if models_ready:
            return {
                "status": "ready",
                "message": "All ML models and database loaded successfully",
                "models": [
                    "resume_scorer",
                    "job_matcher",
                    "salary_predictor",
                    "skill_gap_analyzer"
                ],
                "database": "connected",
                "persistence": "enabled"
            }
        else:
            return {
                "status": "incomplete",
                "message": "Some ML models are not loaded"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "hint": "Run training: python -m app.ml_pipeline.train_models"
        }


@router.get("/user-progress/{user_id}")
async def get_user_progress(user_id: str):
    """Get user progress and statistics from database"""
    try:
        db_service = get_db_service()
        
        # Get progress
        progress = db_service.get_or_create_progress(user_id)
        
        # Get stats
        analyses = db_service.get_user_analyses(user_id, limit=100)
        matches = db_service.get_user_matches(user_id, limit=100)
        skill_gaps = db_service.get_user_skill_gaps(user_id, limit=100)
        
        # Calculate average scores
        valid_analyses = [float(a.resume_score) for a in analyses if isinstance(a.resume_score, (int, float))]
        avg_resume_score = sum(valid_analyses) / len(valid_analyses) if valid_analyses else 0.0
        
        valid_matches = [float(m.match_score) for m in matches if isinstance(m.match_score, (int, float))]
        avg_match_score = sum(valid_matches) / len(valid_matches) if valid_matches else 0.0
        
        # Check if last_study_date is today, if not, reset hours
        today = date.today()
        if getattr(progress, "last_study_date", None) != today:
            db_service.update_progress(
                user_id,
                study_hours_logged=0.0,
                last_study_date=today
            )

        return {
            "user_id": user_id,
            "job_readiness_score": progress.job_readiness_score,
            "resumes_analyzed": len(analyses),
            "jobs_matched": len(matches),
            "skill_gaps_analyzed": len(skill_gaps),
            "target_skills": progress.target_skills,
            "skills_learned": progress.skills_learned,
            "learning_pace": progress.learning_pace,
            "daily_study_hours_goal": progress.daily_study_hours_goal,
            "study_hours_logged": getattr(progress, "study_hours_logged", 0.0),
            "avg_resume_score": round(avg_resume_score, 2),
            "avg_match_score": round(avg_match_score, 2),
            "last_activity": progress.last_activity.isoformat() if progress.last_activity else None,
            "created_at": progress.created_at.isoformat() if progress.created_at else None,
        }
    except Exception as e:
        logger.error(f"❌ Error getting user progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user-progress/{user_id}/log-hours")
async def log_study_hours(user_id: str, request: LogHoursRequest):
    """Log daily study hours"""
    try:
        from datetime import date, datetime
        db_service = get_db_service()
        progress = db_service.get_or_create_progress(user_id)
        
        today = date.today()
        if getattr(progress, "last_study_date", None) != today:
            new_hours = request.hours
        else:
            new_hours = getattr(progress, "study_hours_logged", 0.0) + request.hours
            
        updated = db_service.update_progress(
            user_id,
            study_hours_logged=new_hours,
            last_study_date=today
        )
        return {"success": True, "study_hours_logged": updated.study_hours_logged}
    except Exception as e:
        logger.error(f"❌ Error logging hours: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user-progress/{user_id}/complete-skill")
async def complete_skill(user_id: str, request: CompleteSkillRequest):
    """Mark a target skill as completed"""
    try:
        from datetime import datetime, date, date
        db_service = get_db_service()
        progress = db_service.get_or_create_progress(user_id)
        
        skill = request.skill
        
        # Remove from target, add to learned
        raw_target = getattr(progress, "target_skills", [])
        raw_learned = getattr(progress, "skills_learned", [])
        target_skills = list(raw_target) if raw_target else []  # type: ignore
        skills_learned = list(raw_learned) if raw_learned else []  # type: ignore
        
        if skill in target_skills:
            target_skills.remove(skill)
            
        if skill not in skills_learned:
            skills_learned.append(skill)
            
        # Update progress score a bit (mock logic)
        new_score = min(100.0, float(getattr(progress, "job_readiness_score", 0.0)) + 5.0)  # type: ignore
        
        db_service.update_progress(
            user_id,
            job_readiness_score=new_score,
            target_skills=target_skills,
            skills_learned=skills_learned
        )
        
        return {"success": True, "target_skills": target_skills, "skills_learned": skills_learned}
    except Exception as e:
        logger.error(f"❌ Error completing skill: {e}")
        raise HTTPException(status_code=500, detail=str(e))
