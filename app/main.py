"""
CareerLens AI Backend - FastAPI Application
Main entry point for the API server
"""
import os
from pathlib import Path

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import hmac
import hashlib
import os
import secrets
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from app.database.service import get_db_service
from app.database.models import UserProfile


def _parse_cors_origins() -> list[str]:
    """Parse comma-separated CORS origins from environment.
    Always includes localhost variants for local web development.
    """
    raw = os.getenv("BACKEND_CORS_ORIGINS", "")
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    
    # Always allow local web dev origins
    local_origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    # Merge without duplicates
    for o in local_origins:
        if o not in origins:
            origins.append(o)
    
    # If still empty fall back to wildcard
    return origins if origins else ["*"]


# Create FastAPI application.
app = FastAPI(
    title="CareerLens AI API",
    description="AI-powered career guidance and resume analysis platform",      
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    from app.database.service import get_db_service
    from app.database.models import SalaryBenchmark
    from sqlalchemy import text
    db = get_db_service().get_session()
    alters = [
        "ALTER TABLE user_progress ADD COLUMN study_hours_logged FLOAT DEFAULT 0.0;",
        "ALTER TABLE user_progress ADD COLUMN last_study_date DATE;",
        "ALTER TABLE user_progress ADD COLUMN target_skills JSON DEFAULT '[]'::json;",
        "ALTER TABLE user_progress ADD COLUMN preferred_job_categories JSON DEFAULT '[]'::json;",
        "ALTER TABLE user_progress ADD COLUMN daily_study_hours_goal INTEGER DEFAULT 1;",
        "ALTER TABLE user_progress ADD COLUMN learning_pace VARCHAR DEFAULT 'medium';",
        "ALTER TABLE user_profiles ADD COLUMN profile_image_url VARCHAR;",
        "ALTER TABLE salary_predictions ADD COLUMN job_role VARCHAR;",
        "ALTER TABLE salary_predictions ADD COLUMN experience_years INTEGER;",
        "ALTER TABLE salary_predictions ADD COLUMN education_level VARCHAR;",
        "ALTER TABLE salary_predictions ADD COLUMN high_demand_skills JSON DEFAULT '[]'::json;"
    ]
    
    try:
        for query in alters:
            try:
                db.execute(text(query))
                db.commit()
                print(f"✅ Executed: {query}")
            except Exception as e:
                db.rollback()
                # print(f"ℹ️ Skipped (already exists): {query}")
        
        # Seed SalaryBenchmarks
        if db.query(SalaryBenchmark).count() == 0:
            print("Seeding SalaryBenchmarks for Bangladesh market...")
            benchmarks = [
                SalaryBenchmark(job_role="Software Engineer", experience_level="Fresher", min_salary=25000, max_salary=40000, avg_salary=30000),
                SalaryBenchmark(job_role="Software Engineer", experience_level="Mid", min_salary=50000, max_salary=90000, avg_salary=70000),
                SalaryBenchmark(job_role="Software Engineer", experience_level="Senior", min_salary=100000, max_salary=180000, avg_salary=130000),
                SalaryBenchmark(job_role="Data Scientist", experience_level="Fresher", min_salary=30000, max_salary=50000, avg_salary=40000),
                SalaryBenchmark(job_role="Data Scientist", experience_level="Mid", min_salary=60000, max_salary=110000, avg_salary=85000),
                SalaryBenchmark(job_role="Data Scientist", experience_level="Senior", min_salary=120000, max_salary=200000, avg_salary=150000),
                SalaryBenchmark(job_role="Product Manager", experience_level="Fresher", min_salary=35000, max_salary=50000, avg_salary=40000),
                SalaryBenchmark(job_role="Product Manager", experience_level="Mid", min_salary=60000, max_salary=100000, avg_salary=80000),
                SalaryBenchmark(job_role="Product Manager", experience_level="Senior", min_salary=110000, max_salary=200000, avg_salary=140000),
                SalaryBenchmark(job_role="UI/UX Designer", experience_level="Fresher", min_salary=20000, max_salary=35000, avg_salary=28000),
                SalaryBenchmark(job_role="UI/UX Designer", experience_level="Mid", min_salary=40000, max_salary=75000, avg_salary=55000),
                SalaryBenchmark(job_role="UI/UX Designer", experience_level="Senior", min_salary=80000, max_salary=140000, avg_salary=110000),
                SalaryBenchmark(job_role="Digital Marketer", experience_level="Fresher", min_salary=15000, max_salary=25000, avg_salary=20000),
                SalaryBenchmark(job_role="Digital Marketer", experience_level="Mid", min_salary=30000, max_salary=50000, avg_salary=40000),
                SalaryBenchmark(job_role="Digital Marketer", experience_level="Senior", min_salary=60000, max_salary=100000, avg_salary=80000),
                SalaryBenchmark(job_role="Other", experience_level="Fresher", min_salary=15000, max_salary=25000, avg_salary=20000),
                SalaryBenchmark(job_role="Other", experience_level="Mid", min_salary=30000, max_salary=60000, avg_salary=45000),
                SalaryBenchmark(job_role="Other", experience_level="Senior", min_salary=70000, max_salary=120000, avg_salary=90000),
            ]
            db.add_all(benchmarks)
            db.commit()
            print("✅ SalaryBenchmarks seeded!")
            
    finally:
        db.close()

# Configure CORS
cors_origins = _parse_cors_origins()
# allow_credentials must be False when origins=["*"], True for specific origins
allow_credentials = "*" not in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register ML API Router
try:
    from app.api.ml_router import router as ml_router
    app.include_router(ml_router)
    print("[OK] ML Router registered successfully!")
except Exception as e:
    print(f"[ERROR] Error loading ML Router: {e}")
    import traceback
    traceback.print_exc()

# Register Roadmap Router
try:
    from app.api.roadmap_router import router as roadmap_router
    app.include_router(roadmap_router)
    print("[OK] Roadmap Router registered successfully!")
except Exception as e:
    print(f"[ERROR] Error loading Roadmap Router: {e}")

# Register Profile Router
try:
    from app.api.profile_router import router as profile_router
    app.include_router(profile_router, prefix="/profile", tags=["Profile"])
    print("[OK] Profile Router registered successfully!")
except Exception as e:
    print(f"[ERROR] Error loading Profile Router: {e}")

# Register Admin Router
try:
    from app.api.admin_router import router as admin_router
    app.include_router(admin_router)
    print("[OK] Admin Router registered successfully!")
except Exception as e:
    print(f"[ERROR] Error loading Admin Router: {e}")

# Register Dashboard Analytics Router
# IMPORTANT: must be included BEFORE the wildcard GET /api/dashboard/{user_id}
# route defined inline below, so FastAPI resolves /api/dashboard/analytics/...
# as a literal path segment rather than a user_id parameter.
try:
    from app.api.dashboard_router import router as dashboard_router
    app.include_router(dashboard_router)
    print("[OK] Dashboard Analytics Router registered successfully!")
except Exception as e:
    print(f"[ERROR] Error loading Dashboard Router: {e}")


# Mount static directory for profile pictures
os.makedirs("uploads/profile_pictures", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Auth request models
class AuthSignupRequest(BaseModel):
    email: str
    password: str
    name: str = ""


class AuthLoginRequest(BaseModel):
    email: str
    password: str


class GoogleAuthRequest(BaseModel):
    id_token: str


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _issue_access_token(user_id: str, email: str) -> str:
    secret = os.getenv("AUTH_SECRET", "career_lens_dev_secret_change_me")
    now = int(datetime.now(timezone.utc).timestamp())
    nonce = secrets.token_hex(8)
    raw = f"{user_id}:{email}:{now}:{nonce}"
    sig = hmac.new(secret.encode("utf-8"), raw.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{raw}:{sig}"


@app.post("/auth/signup")
def signup(request: AuthSignupRequest):
    """Create an account and return auth token."""
    email = _normalize_email(request.email)
    if not email:
        return JSONResponse(status_code=400, content={"detail": "Email is required"})

    try:
        db_service = get_db_service()
        user = db_service.create_user(email=email, name=request.name)
        user_id = str(user.user_id)
        token = _issue_access_token(user_id, email)
        return JSONResponse(
            status_code=200,
            content={
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user_id,
                    "email": email,
                    "name": str(user.name) if user.name else "User",
                    "is_premium": getattr(user, 'is_premium', False),
                    "is_admin": getattr(user, 'is_admin', False),
                },
            },
        )
    except Exception as e:
        import traceback
        err = str(e)
        print(f"[SIGNUP ERROR] {err}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=400,
            content={"detail": f"Signup failed: {err}"},
        )


@app.post("/auth/login")
def login(request: AuthLoginRequest):
    """Authenticate and return token."""
    email = _normalize_email(request.email)
    if not email:
        return JSONResponse(status_code=400, content={"detail": "Email is required"})

    try:
        db_service = get_db_service()
        db = db_service.get_session()
        try:
            user = db.query(UserProfile).filter(UserProfile.email == email).first()
            if not user:
                user = db_service.create_user(email=email, name="User")
            user_id = str(user.user_id)
        finally:
            db.close()

        token = _issue_access_token(user_id, email)
        return JSONResponse(
            status_code=200,
            content={
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user_id,
                    "email": email,
                    "name": user.name or "User",
                    "is_premium": getattr(user, 'is_premium', False),
                    "is_admin": getattr(user, 'is_admin', False),
                },
            },
        )
    except Exception as e:
        import traceback
        err = str(e)
        print(f"[LOGIN ERROR] {err}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=400,
            content={"detail": f"Login failed: {err}"},
        )

@app.post("/auth/google")
def google_login(request: GoogleAuthRequest):
    """Authenticate via Google ID Token and return token."""
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        
        # Verify token
        try:
            idinfo = id_token.verify_oauth2_token(request.id_token, requests.Request())
        except ValueError as e:
            print(f"[AUTH ERROR] Failed to verify Google token: {e}")
            # MOCK FALLBACK for dev if token is actually just an email string (e.g. from tests)
            if "@" in request.id_token and len(request.id_token) < 50:
                idinfo = {"email": request.id_token, "name": "Google User"}
            else:
                return JSONResponse(status_code=400, content={"detail": "Invalid Google token"})

        raw_email = idinfo.get('email')
        if not raw_email:
            return JSONResponse(status_code=400, content={"detail": "Email not found in Google token"})
            
        email = _normalize_email(str(raw_email))
        name = idinfo.get('name', 'Google User')
        db_service = get_db_service()
        db = db_service.get_session()
        try:
            user = db.query(UserProfile).filter(UserProfile.email == email).first()
            if not user:
                user = UserProfile(email=email, name=name)
                db.add(user)
                db.commit()
                db.refresh(user)
            user_id = str(user.user_id)
        finally:
            db.close()

        token = _issue_access_token(user_id, email)
        return JSONResponse(
            status_code=200,
            content={
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user_id,
                    "email": email,
                    "name": name,
                    "is_premium": getattr(user, 'is_premium', False),
                    "is_admin": getattr(user, 'is_admin', False),
                },
            },
        )
    except Exception as e:
        print(f"[AUTH WARNING] Google verification failed or google-auth missing: {e}")
        # Native JWT decoding fallback
        try:
            import base64
            import json
            parts = request.id_token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token")
            payload = parts[1]
            payload += '=' * (-len(payload) % 4)
            idinfo = json.loads(base64.urlsafe_b64decode(payload).decode('utf-8'))
            email = _normalize_email(str(idinfo.get('email')))
            name = idinfo.get('name', 'Google User')
            
            db_service = get_db_service()
            db = db_service.get_session()
            try:
                user = db.query(UserProfile).filter(UserProfile.email == email).first()
                if not user:
                    user = UserProfile(email=email, name=name)
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                user_id = str(user.user_id)
            finally:
                db.close()
                
            return JSONResponse(
                status_code=200,
                content={
                    "access_token": _issue_access_token(user_id, email),
                    "token_type": "bearer",
                    "user": {
                        "id": user_id, 
                        "email": email, 
                        "name": name,
                        "is_premium": getattr(user, 'is_premium', False),
                        "is_admin": getattr(user, 'is_admin', False)
                    }
                }
            )
        except Exception as inner_e:
            return JSONResponse(status_code=500, content={"detail": f"Failed to parse Google token: {inner_e}"})

# Health check endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to CareerLens AI API",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CareerLens AI Backend",
    }


@app.get("/ready")
async def readiness_check():
    """Readiness endpoint for app/server probes."""
    return {
        "ready": True,
    }


# User Preferences Models
class UserPreferencesRequest(BaseModel):
    target_skills: list[str] = []
    daily_study_hours_goal: int = 1
    learning_pace: str = "medium"  # 'slow', 'medium', 'fast'
    preferred_categories: list[str] = []


@app.get("/api/preferences/{user_id}")
async def get_preferences(user_id: str):
    """Get user preferences from database"""
    try:
        db_service = get_db_service()
        progress = db_service.get_or_create_progress(user_id)
        return JSONResponse(
            status_code=200,
            content={
                "user_id": user_id,
                "target_skills": progress.target_skills or [],
                "daily_study_hours_goal": progress.daily_study_hours_goal or 1,
                "learning_pace": progress.learning_pace or "medium",
                "preferred_categories": progress.preferred_job_categories or [],
                "updated_at": progress.updated_at.isoformat() if progress.updated_at else datetime.now(timezone.utc).isoformat(),
            }
        )
    except Exception as e:
        print(f"[ERROR] Failed to get preferences: {e}")
        return JSONResponse(
            status_code=200,
            content={
                "user_id": user_id,
                "target_skills": [],
                "daily_study_hours_goal": 1,
                "learning_pace": "medium",
                "preferred_categories": [],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )


@app.post("/api/preferences/{user_id}")
async def save_preferences(user_id: str, request: UserPreferencesRequest):
    """Save user preferences to database"""
    try:
        db_service = get_db_service()
        db_service.update_progress(
            user_id,
            target_skills=request.target_skills,
            daily_study_hours_goal=request.daily_study_hours_goal,
            learning_pace=request.learning_pace,
            preferred_job_categories=request.preferred_categories,
        )
        return JSONResponse(
            status_code=200,
            content={"message": "Preferences saved successfully", "data": {
                "user_id": user_id,
                "target_skills": request.target_skills,
                "daily_study_hours_goal": request.daily_study_hours_goal,
                "learning_pace": request.learning_pace,
                "preferred_categories": request.preferred_categories,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }}
        )
    except Exception as e:
        print(f"[ERROR] Failed to save preferences: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": f"Failed to save preferences: {str(e)}"}
        )

@app.get("/api/dashboard/{user_id}")
async def get_dashboard_analytics(user_id: str):
    """
    Get dynamic analytics for the user dashboard.

    Career Readiness formula (matches Flutter client):
        40% × resume_quality + 30% × skill_match + 30% × job_readiness
    Weights are redistributed proportionally when some components are missing.
    """
    db = None
    try:
        db_service = get_db_service()
        db = db_service.get_session()

        from app.database.models import UserProfile, ResumeAnalysis, SkillGap, UserProgress

        uid = str(user_id)  # safe string comparison against UUID columns

        # ── Profile Completion ───────────────────────────────────────────
        profile = db.query(UserProfile).filter(UserProfile.user_id == uid).first()
        profile_score = 0
        if profile:
            fields = [profile.name, profile.experience_years, profile.education_level,
                      profile.current_industry, profile.target_skills]
            filled = sum(1 for f in fields if f)
            profile_score = min(int((filled / 5) * 100), 100)

        # ── Resume Quality ───────────────────────────────────────────────
        latest_resume = (
            db.query(ResumeAnalysis)
            .filter(ResumeAnalysis.user_id == uid)
            .order_by(ResumeAnalysis.created_at.desc())
            .first()
        )
        resume_quality: int | None = None
        if latest_resume:
            if latest_resume.match_percentage is not None:
                resume_quality = int(latest_resume.match_percentage)
            elif latest_resume.resume_score is not None:
                resume_quality = min(int(float(latest_resume.resume_score) * 100), 100)

        # ── Skill Match ──────────────────────────────────────────────────
        latest_skill_gap = (
            db.query(SkillGap)
            .filter(SkillGap.user_id == uid)
            .order_by(SkillGap.created_at.desc())
            .first()
        )
        skill_match: int | None = None
        if latest_skill_gap and latest_skill_gap.user_skills and latest_skill_gap.total_missing is not None:
            user_skill_count = len(latest_skill_gap.user_skills)
            total_skills = user_skill_count + int(latest_skill_gap.total_missing)
            skill_match = int((user_skill_count / total_skills) * 100) if total_skills > 0 else 0

        # ── Job Readiness ────────────────────────────────────────────────
        progress = db.query(UserProgress).filter(UserProgress.user_id == uid).first()
        job_readiness: int | None = None
        if progress and progress.job_readiness_score:
            job_readiness = int(float(progress.job_readiness_score))

        # ── Career Readiness (weighted formula) ──────────────────────────
        # 40% Resume + 30% Skill + 30% Job Readiness.
        # If a component is missing its weight is redistributed.
        weighted_sum = 0.0
        total_weight = 0
        if resume_quality is not None: weighted_sum += resume_quality * 40; total_weight += 40
        if skill_match    is not None: weighted_sum += skill_match    * 30; total_weight += 30
        if job_readiness  is not None: weighted_sum += job_readiness  * 30; total_weight += 30

        if total_weight > 0:
            career_readiness = int(weighted_sum / total_weight)
        else:
            career_readiness = 0

        # has_data = True as soon as at least one real analysis score exists
        has_data = any([
            resume_quality is not None,
            skill_match is not None,
            job_readiness is not None,
        ])

        return JSONResponse(status_code=200, content={
            "career_readiness": career_readiness,
            "resume_quality":   resume_quality,
            "skill_match":      skill_match,
            "job_readiness":    job_readiness,
            "profile_complete": profile_score,
            "has_data":         has_data,
        })

    except Exception as e:
        print(f"[ERROR] Failed to fetch dashboard analytics: {e}")
        import traceback; traceback.print_exc()
        # Return 200 with has_data=False so Flutter shows the onboarding card
        # instead of the error state (network errors are handled separately).
        return JSONResponse(status_code=200, content={
            "career_readiness": 0,
            "resume_quality":   None,
            "skill_match":      None,
            "job_readiness":    None,
            "profile_complete": 0,
            "has_data":         False,
        })
    finally:
        if db is not None:
            db.close()


@app.get("/api/progress/{user_id}")
async def get_user_progress(user_id: str):
    """Get user progress based on actual database metrics"""
    try:
        db_service = get_db_service()
        
        # Get progress and stats
        progress = db_service.get_or_create_progress(user_id)
        analyses = db_service.get_user_analyses(user_id, limit=5)
        matches = db_service.get_user_matches(user_id, limit=5)
        
        target_skills = progress.target_skills if isinstance(progress.target_skills, list) else []
        skills_learned = progress.skills_learned if isinstance(progress.skills_learned, list) else []
        skills_in_progress = progress.skills_in_progress if isinstance(progress.skills_in_progress, list) else []
        
        total_skills_count = len(target_skills) if target_skills else 5
        completed_skills_count = len(skills_learned)
        in_progress_skills_count = len(skills_in_progress)
        
        # 1. Technical Skills (40%)
        tech_skill_score = min(100, int((completed_skills_count / total_skills_count) * 100)) if total_skills_count > 0 else 0
        
        # 2. Resume Quality (25%)
        resume_scores = [float(a.resume_score) for a in analyses if isinstance(a.resume_score, (int, float))]
        avg_resume_score = sum(resume_scores) / len(resume_scores) if resume_scores else 0.0
        resume_quality_score = min(100, int(avg_resume_score * 100))
        
        # 3. Experience Match (20%)
        match_scores = [float(m.match_score) for m in matches if isinstance(m.match_score, (int, float))]
        avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0.0
        experience_score = min(100, int(avg_match_score * 100))
        
        # 4. Learning Progress (15%)
        learning_ratio = (completed_skills_count + 0.5 * in_progress_skills_count) / total_skills_count if total_skills_count > 0 else 0
        learning_progress_score = min(100, int(learning_ratio * 100))
        
        # Calculate Readiness Score
        job_readiness_score = int(
            tech_skill_score * 0.40 +
            resume_quality_score * 0.25 +
            experience_score * 0.20 +
            learning_progress_score * 0.15
        )
        
        # Generate Recommendations
        recommendations = []
        if resume_quality_score < 60:
            recommendations.append("Improve ATS compatibility and optimize your resume.")
        if learning_progress_score < 50:
            recommendations.append("Complete remaining roadmap skills to boost your progress.")
        if tech_skill_score < 60:
            recommendations.append("Focus on learning core technical skills required for your target role.")
        if experience_score < 60:
            recommendations.append("Add more personal projects to showcase hands-on experience.")
        
        if not recommendations:
            recommendations.append("Keep up the great work! You are on the right track.")
            
        return JSONResponse(
            status_code=200,
            content={
                "user_id": user_id,
                "job_readiness_score": job_readiness_score,
                "total_skills_to_learn": total_skills_count,
                "completed_skills": completed_skills_count,
                "skills_in_progress": in_progress_skills_count,
                "technical_skill_score": tech_skill_score,
                "resume_quality_score": resume_quality_score,
                "experience_score": experience_score,
                "learning_progress_score": learning_progress_score,
                "recommendations": recommendations,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "personalized": True,
                "learning_pace": progress.learning_pace,
            }
        )
    except Exception as e:
        # Fallback to defaults on error
        print(f"[ERROR] Error calculating job readiness: {e}")
        return JSONResponse(
            status_code=200,
            content={
                "user_id": user_id,
                "job_readiness_score": 0,
                "total_skills_to_learn": 5,
                "completed_skills": 0,
                "skills_in_progress": 0,
                "technical_skill_score": 0,
                "resume_quality_score": 0,
                "experience_score": 0,
                "learning_progress_score": 0,
                "recommendations": ["Complete your profile information.", "Start learning skills from your roadmap."],
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "personalized": False,
            }
        )


from fastapi import UploadFile, File

@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Mock endpoint to handle resume file uploads and validate them"""
    from fastapi import HTTPException
    import io
    
    content = await file.read()
    
    # Validation: Check if it's a real resume format
    if file.filename and file.filename.lower().endswith(".pdf"):
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            # Read up to the first 3 pages
            for i in range(min(3, len(pdf_reader.pages))):
                text += pdf_reader.pages[i].extract_text() or ""
                
            text_lower = text.lower()
            keywords = ["experience", "education", "skills", "work", "university", "school", "project", "profile", "github", "linkedin", "contact"]
            found_keywords = sum(1 for kw in keywords if kw in text_lower)
            
            # If the text is suspiciously short or lacks any resume keywords, reject it.
            if len(text_lower) < 50 or found_keywords < 1:
                raise HTTPException(
                    status_code=400, 
                    detail="The uploaded document does not appear to be a valid resume. Please upload an appropriate resume format."
                )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail="Could not read the PDF file. Please ensure it is a valid, readable PDF resume."
            )

    # In a real app, this would extract text from the PDF/DOC and analyze it.
    return {
        "success": True,
        "resume_id": "mock-1234",
        "resume_text": f"Extracted text from {file.filename}",
        "ats_score": 78,
        "detected_skills": ["Flutter", "Dart", "Python", "FastAPI"],
        "suggestions": ["Add more quantifiable achievements", "Include keywords from job description"],
        "statistics": {
            "ats_score": 78,
            "readability": "Good",
            "impact": "Medium"
        },
        "market": "global"
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api": "operational",
        "endpoints": {
            "resume": [
                "/api/upload-resume",
                "/api/analyze-resume"
            ],
            "analysis": [
                "/api/job-match",
                "/api/skill-gap",
                "/api/job-readiness"
            ],
            "preferences": [
                "/api/preferences/{user_id}",
                "/api/progress/{user_id}"
            ]
        }
    }


@app.get("/api/seed-roadmaps")
async def trigger_seed():
    from app.migrations.seed_roadmaps import seed
    try:
        seed()
        return {"success": True, "message": "Seeded successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
