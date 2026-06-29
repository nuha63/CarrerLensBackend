"""
Roadmap Service - CRUD operations and recommendation logic for Career Roadmaps
"""
import logging
from typing import Optional, List
from datetime import datetime, timezone

from app.database.service import get_db_service
from app.database.models import (
    CareerPath, RoadmapPhase, RoadmapSkill, UserSkillProgress,
    UserProgress, SkillGap
)

logger = logging.getLogger(__name__)


# Keyword mapping: career name keywords -> roadmap career_name
_CATEGORY_KEYWORD_MAP = {
    "machine learning": "Machine Learning Engineer",
    "ml engineer": "Machine Learning Engineer",
    "data scientist": "Data Scientist",
    "data science": "Data Scientist",
    "flutter": "Flutter Developer",
    "android": "Android Developer",
    "backend": "Backend Developer",
    "back-end": "Backend Developer",
    "full stack": "Full Stack Developer",
    "fullstack": "Full Stack Developer",
    "ui/ux": "UI/UX Designer",
    "ui ux": "UI/UX Designer",
    "design": "UI/UX Designer",
    "cybersecurity": "Cybersecurity Analyst",
    "security": "Cybersecurity Analyst",
    "devops": "DevOps Engineer",
    "qa": "QA Engineer",
    "quality assurance": "QA Engineer",
    "testing": "QA Engineer",
}

# Skill -> career mapping for skill-gap-based recommendations
_SKILL_CAREER_MAP = {
    "python": "Machine Learning Engineer",
    "tensorflow": "Machine Learning Engineer",
    "pytorch": "Machine Learning Engineer",
    "scikit-learn": "Machine Learning Engineer",
    "machine learning": "Machine Learning Engineer",
    "deep learning": "Machine Learning Engineer",
    "sql": "Data Scientist",
    "pandas": "Data Scientist",
    "numpy": "Data Scientist",
    "r": "Data Scientist",
    "flutter": "Flutter Developer",
    "dart": "Flutter Developer",
    "kotlin": "Android Developer",
    "java": "Android Developer",
    "android sdk": "Android Developer",
    "node.js": "Backend Developer",
    "nodejs": "Backend Developer",
    "fastapi": "Backend Developer",
    "django": "Backend Developer",
    "flask": "Backend Developer",
    "postgresql": "Backend Developer",
    "react": "Full Stack Developer",
    "vue": "Full Stack Developer",
    "angular": "Full Stack Developer",
    "javascript": "Full Stack Developer",
    "figma": "UI/UX Designer",
    "adobe xd": "UI/UX Designer",
    "sketch": "UI/UX Designer",
    "linux": "Cybersecurity Analyst",
    "penetration testing": "Cybersecurity Analyst",
    "network security": "Cybersecurity Analyst",
    "docker": "DevOps Engineer",
    "kubernetes": "DevOps Engineer",
    "ci/cd": "DevOps Engineer",
    "selenium": "QA Engineer",
    "pytest": "QA Engineer",
    "test automation": "QA Engineer",
}


class RoadmapService:
    """Service layer for all roadmap-related database operations."""

    def __init__(self):
        self._db_service = get_db_service()

    def _session(self):
        return self._db_service.get_session()

    # ─────────────────────────────────────────────
    # READ: all roadmaps
    # ─────────────────────────────────────────────
    def get_all_roadmaps(self) -> List[CareerPath]:
        """Return all career paths (without phases for listing)."""
        db = self._session()
        try:
            return db.query(CareerPath).order_by(CareerPath.name).all()
        finally:
            db.close()

    # ─────────────────────────────────────────────
    # READ: single roadmap + phases
    # ─────────────────────────────────────────────
    def get_roadmap_by_id(self, roadmap_id: int) -> Optional[CareerPath]:
        """Return a single roadmap with all its phases eagerly loaded."""
        db = self._session()
        try:
            roadmap = db.query(CareerPath).filter(CareerPath.id == roadmap_id).first()
            if roadmap:
                # Eagerly access phases and skills while session is open
                for phase in roadmap.phases:
                    _ = phase.skills
            return roadmap
        finally:
            db.close()

    def get_roadmap_by_name(self, career_name: str) -> Optional[CareerPath]:
        """Return roadmap by exact career name."""
        db = self._session()
        try:
            roadmap = db.query(CareerPath).filter(
                CareerPath.name == career_name
            ).first()
            if roadmap:
                for phase in roadmap.phases:
                    _ = phase.skills
            return roadmap
        finally:
            db.close()

    # ─────────────────────────────────────────────
    # RECOMMENDATION
    # ─────────────────────────────────────────────
    def get_recommended_roadmap(self, user_id: str) -> dict:
        """
        Recommend a roadmap based on:
        1. User's preferred_job_categories (UserProgress)
        2. User's missing skills from latest SkillGap analysis
        Falls back to 'Machine Learning Engineer' if nothing matches.
        """
        db = self._session()
        try:
            # Step 1: Try preferred job categories
            progress = db.query(UserProgress).filter(
                UserProgress.user_id == user_id
            ).first()

            recommended_career: Optional[str] = None
            reason: str = "Based on your profile preferences"
            highlighted_skills: List[str] = []

            if progress and progress.preferred_job_categories:
                for category in progress.preferred_job_categories:
                    cat_lower = category.lower()
                    for keyword, career in _CATEGORY_KEYWORD_MAP.items():
                        if keyword in cat_lower:
                            recommended_career = career
                            reason = f"Recommended because of your preferred job category: {category}"
                            break
                    if recommended_career:
                        break

            # Step 2: Try skill gap analysis
            if not recommended_career:
                latest_gap = db.query(SkillGap).filter(
                    SkillGap.user_id == user_id
                ).order_by(SkillGap.created_at.desc()).first()

                if latest_gap and latest_gap.missing_skills:
                    skill_votes: dict[str, int] = {}
                    for skill in latest_gap.missing_skills:
                        skill_lower = skill.lower()
                        for keyword, career in _SKILL_CAREER_MAP.items():
                            if keyword in skill_lower:
                                skill_votes[career] = skill_votes.get(career, 0) + 1
                                highlighted_skills.append(skill)
                                break

                    if skill_votes:
                        recommended_career = max(skill_votes, key=lambda k: skill_votes[k])
                        reason = "Recommended because of your skill gap analysis"

            # Step 3: Default fallback
            if not recommended_career:
                recommended_career = "Machine Learning Engineer"
                reason = "Popular career path for getting started"

            # Fetch the roadmap
            roadmap = db.query(CareerPath).filter(
                CareerPath.name == recommended_career
            ).first()

            if not roadmap:
                roadmap = db.query(CareerPath).first()

            if roadmap:
                for phase in roadmap.phases:
                    _ = phase.skills  # eager load

            return {
                "roadmap": roadmap,
                "reason": reason,
                "highlighted_skills": list(set(highlighted_skills)),
            }
        finally:
            db.close()

    # ─────────────────────────────────────────────
    # ─────────────────────────────────────────────
    # PROGRESS: get completed skills
    # ─────────────────────────────────────────────
    def get_user_skill_progress(self, user_id: str, roadmap_id: int) -> List[int]:
        """
        Return list of completed skill IDs for a user+roadmap.
        """
        db = self._session()
        try:
            roadmap = self.get_roadmap_by_id(roadmap_id)
            if not roadmap:
                return []
            
            completed_skill_ids = []
            
            for phase in roadmap.phases:
                if not phase.skills:
                    continue
                    
                skill_ids = [s.id for s in phase.skills]
                completed_records = db.query(UserSkillProgress).filter(
                    UserSkillProgress.user_id == user_id,
                    UserSkillProgress.skill_id.in_(skill_ids),
                    UserSkillProgress.is_completed == True
                ).all()
                
                completed_skill_ids.extend([r.skill_id for r in completed_records])
                    
            return completed_skill_ids
        finally:
            db.close()

    # ─────────────────────────────────────────────
    # PROGRESS: mark/unmark skill
    # ─────────────────────────────────────────────
    def set_skill_completion(
        self, user_id: str, skill_id: int, is_completed: bool
    ) -> bool:
        """
        Set a specific skill to completed or not completed.
        """
        db = self._session()
        try:
            record = db.query(UserSkillProgress).filter(
                UserSkillProgress.user_id == user_id,
                UserSkillProgress.skill_id == skill_id
            ).first()

            if not record:
                record = UserSkillProgress(
                    user_id=user_id,
                    skill_id=skill_id,
                )
                db.add(record)

            record.is_completed = is_completed  # type: ignore
            record.completed_at = datetime.now(timezone.utc) if is_completed else None  # type: ignore

            db.commit()
            logger.info(
                f"✅ Skill {skill_id} marked {'complete' if is_completed else 'incomplete'} "
                f"for user {user_id}"
            )
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error setting skill completion: {e}")
            raise
        finally:
            db.close()



# Singleton
_roadmap_service_instance = None


def get_roadmap_service() -> RoadmapService:
    """Get or create RoadmapService singleton."""
    global _roadmap_service_instance
    if _roadmap_service_instance is None:
        _roadmap_service_instance = RoadmapService()
    return _roadmap_service_instance
