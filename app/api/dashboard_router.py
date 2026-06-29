"""
Dashboard Analytics Router
Endpoint: GET /api/dashboard/analytics/{user_id}

Returns a rich analytics payload for the Flutter dashboard.
All scores are integers 0-100. Null means the data source has
not been populated yet (e.g. user has never run a skill-gap).

Career Readiness formula:
    career_readiness = 0.4 × resume_quality
                     + 0.3 × skill_match
                     + 0.3 × job_readiness
Weights are redistributed proportionally when some components are missing.
"""
from __future__ import annotations

import traceback
from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.database.service import get_db_service

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard Analytics"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Helper – clamp a float/int to 0-100 integer
# ─────────────────────────────────────────────────────────────────────────────
def _pct(value: float | int) -> int:
    return max(0, min(100, int(value)))


# ─────────────────────────────────────────────────────────────────────────────
# Helper – profile completion %
# Fields considered: name, email, resume uploaded, target_skills,
#                    education_level, experience_years
# ─────────────────────────────────────────────────────────────────────────────
def _profile_completion(profile, has_resume: bool) -> int:
    if profile is None:
        return 0
    checks = [
        bool(profile.name and profile.name.strip()),
        bool(profile.email and profile.email.strip()),
        has_resume,
        bool(profile.target_skills),          # non-empty list
        bool(profile.education_level and profile.education_level.strip()),
        bool(profile.experience_years is not None and profile.experience_years > 0),
    ]
    return _pct((sum(checks) / len(checks)) * 100)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/dashboard/analytics/{user_id}
# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/analytics/{user_id}",
    summary="Get dashboard analytics for a user",
    response_description="Analytics payload with career readiness scores",
    responses={
        200: {
            "description": "Analytics data (has_resume=false when no resume uploaded)",
            "content": {
                "application/json": {
                    "examples": {
                        "no_resume": {
                            "summary": "New user – no resume uploaded",
                            "value": {
                                "has_resume": False,
                                "message": "Upload a resume to generate insights.",
                            },
                        },
                        "with_data": {
                            "summary": "User with full analysis history",
                            "value": {
                                "has_resume": True,
                                "resume_quality": 82,
                                "skill_match": 74,
                                "job_readiness": 78,
                                "profile_completion": 90,
                                "career_readiness": 79,
                                "has_data": True,
                            },
                        },
                    }
                }
            },
        },
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_dashboard_analytics(user_id: str):
    """
    Retrieve career analytics for the dashboard.

    **Logic**:
    1. Verify the user exists in `user_profiles`.
    2. Check whether a resume has been uploaded to `user_resumes`.
    3. If **no resume** → return `has_resume: false`.
    4. If **resume exists** → collect scores from:
       - `resume_analyses` → `resume_quality`
       - `job_matches`     → `skill_match` (best match score)
       - `skill_gaps`      → refines `skill_match` using user vs missing skills
       - `user_progress`   → `job_readiness`
       - `user_profiles`   → `profile_completion`
    5. Compute `career_readiness = 0.4×RQ + 0.3×SM + 0.3×JR` (weights
       redistributed proportionally for missing components).
    """
    db = None
    try:
        db_service = get_db_service()
        db = db_service.get_session()

        from app.database.models import (
            UserProfile, UserResume, ResumeAnalysis,
            JobMatch, SkillGap, UserProgress,
        )

        uid = str(user_id)

        # ── 1. Verify user exists ────────────────────────────────────────
        profile = (
            db.query(UserProfile)
            .filter(UserProfile.user_id == uid)
            .first()
        )
        if profile is None:
            return JSONResponse(
                status_code=404,
                content={"detail": f"User '{uid}' not found."},
            )

        # ── 2. Check for uploaded resume ─────────────────────────────────
        latest_uploaded_resume = (
            db.query(UserResume)
            .filter(UserResume.user_id == uid)
            .order_by(UserResume.created_at.desc())
            .first()
        )
        has_resume = latest_uploaded_resume is not None

        if not has_resume:
            return JSONResponse(
                status_code=200,
                content={
                    "has_resume": False,
                    "message": "Upload a resume to generate insights.",
                },
            )

        # ── 3. Resume Quality ────────────────────────────────────────────
        # Source: latest ResumeAnalysis row.
        # Prefer match_percentage (0-100 int) over resume_score (0-1 float).
        latest_analysis = (
            db.query(ResumeAnalysis)
            .filter(ResumeAnalysis.user_id == uid)
            .order_by(ResumeAnalysis.created_at.desc())
            .first()
        )
        resume_quality: int | None = None
        if latest_analysis:
            if latest_analysis.match_percentage is not None:
                resume_quality = _pct(latest_analysis.match_percentage)
            elif latest_analysis.resume_score is not None:
                resume_quality = _pct(float(latest_analysis.resume_score) * 100)

        # ── 4. Skill Match ───────────────────────────────────────────────
        # Primary source: SkillGap (user_skills vs missing skills ratio).
        # Fallback: best JobMatch.match_score * 100.
        skill_match: int | None = None

        latest_skill_gap = (
            db.query(SkillGap)
            .filter(SkillGap.user_id == uid)
            .order_by(SkillGap.created_at.desc())
            .first()
        )
        if (
            latest_skill_gap
            and latest_skill_gap.user_skills
            and latest_skill_gap.total_missing is not None
        ):
            user_skill_count = len(latest_skill_gap.user_skills)
            total = user_skill_count + int(latest_skill_gap.total_missing)
            skill_match = _pct((user_skill_count / total) * 100) if total > 0 else 0
        else:
            # Fallback: use best job match score as a proxy for skill fit
            best_job_match = (
                db.query(JobMatch)
                .filter(JobMatch.user_id == uid)
                .order_by(JobMatch.match_score.desc())
                .first()
            )
            if best_job_match and best_job_match.match_score is not None:
                skill_match = _pct(float(best_job_match.match_score) * 100)

        # ── 5. Job Readiness ─────────────────────────────────────────────
        # Source: UserProgress.job_readiness_score (0-100).
        # Fallback: average of resume_quality + skill_match if both exist.
        progress = (
            db.query(UserProgress)
            .filter(UserProgress.user_id == uid)
            .first()
        )
        job_readiness: int | None = None
        if progress and progress.job_readiness_score:
            job_readiness = _pct(float(progress.job_readiness_score))
        elif resume_quality is not None and skill_match is not None:
            # Synthetic fallback: simple average of available scores
            job_readiness = _pct((resume_quality + skill_match) / 2)

        # ── 6. Profile Completion ────────────────────────────────────────
        profile_completion = _profile_completion(profile, has_resume=True)

        # ── 7. Career Readiness (weighted formula) ───────────────────────
        # career_readiness = 0.4×RQ + 0.3×SM + 0.3×JR
        # Missing components are excluded and weights redistributed.
        weighted_sum = 0.0
        total_weight = 0
        if resume_quality is not None:
            weighted_sum += resume_quality * 40
            total_weight += 40
        if skill_match is not None:
            weighted_sum += skill_match * 30
            total_weight += 30
        if job_readiness is not None:
            weighted_sum += job_readiness * 30
            total_weight += 30

        career_readiness = (
            _pct(weighted_sum / total_weight) if total_weight > 0 else 0
        )

        # has_data: True once at least one AI analysis score exists
        has_data = any([
            resume_quality is not None,
            skill_match is not None,
            job_readiness is not None,
        ])

        return JSONResponse(
            status_code=200,
            content={
                "has_resume":        True,
                "has_data":          has_data,
                "resume_quality":    resume_quality,
                "skill_match":       skill_match,
                "job_readiness":     job_readiness,
                "profile_completion": profile_completion,
                "career_readiness":  career_readiness,
                # Extra context fields for rich UI
                "last_analysis_date": (
                    latest_analysis.created_at.isoformat()
                    if latest_analysis and latest_analysis.created_at
                    else None
                ),
                "missing_skills": (
                    latest_skill_gap.missing_skills[:5]
                    if latest_skill_gap and latest_skill_gap.missing_skills
                    else []
                ),
                "priority_skills": (
                    latest_skill_gap.priority_skills[:5]
                    if latest_skill_gap and latest_skill_gap.priority_skills
                    else []
                ),
            },
        )

    except Exception as exc:
        print(f"[ERROR] Dashboard analytics for user '{user_id}': {exc}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": "Failed to load dashboard analytics. Please try again."},
        )
    finally:
        if db is not None:
            db.close()
