"""
Roadmap Router - FastAPI routes for AI Career Roadmap feature
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from starlette.responses import JSONResponse

from app.database.roadmap_service import get_roadmap_service
from app.database.models import CareerPath, RoadmapPhase

router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])
# ─────────────────────────────────────────────────────────
# Helper: serialize models (avoid Pydantic ORM mode issues)
# ─────────────────────────────────────────────────────────

def _serialize_phase(
    phase: RoadmapPhase,
    completed_ids: Optional[List[int]] = None
) -> dict:

    completed_ids = completed_ids or []
    skills_list = [s.skill_name for s in phase.skills] if phase.skills else []
    
    # Generate a simple fallback description if none exists
    description = f"Learn and master the fundamentals of {phase.phase_name}."
    if skills_list:
        description += f" Key topics include: {', '.join(skills_list[:3])}."

    return {
        "id": str(phase.id),
        "roadmap_id": str(phase.career_id),
        "phase_number": phase.phase_order,
        "phase_title": phase.phase_name,
        "phase_description": description,
        "estimated_weeks": 4,
        "completion_percentage": 100 if (phase.id in completed_ids) else 0,
        "key_skills": skills_list,
        "is_completed": phase.id in completed_ids,
        "created_at": None,
    }


def _serialize_roadmap(
    roadmap: CareerPath,
    completed_ids: Optional[List[int]] = None
) -> dict:

    phases = [
        _serialize_phase(p, completed_ids)
        for p in (roadmap.phases or [])
    ]

    total = len(phases)

    done = sum(
        1 for p in phases
        if p["is_completed"]
    )

    overall_pct = int((done / total) * 100) if total > 0 else 0

    return {
        "id": str(roadmap.id),
        "career_name": roadmap.name,
        "description": roadmap.description,
        "estimated_duration": "N/A",
        "icon_name": "work",
        "total_phases": total,
        "completed_phases": done,
        "overall_completion_percentage": overall_pct,
        "phases": phases,
        "created_at": None,
    }
# ─────────────────────────────────────────────────────────
# Pydantic request bodies
# ─────────────────────────────────────────────────────────

class PhaseProgressRequest(BaseModel):
    roadmap_id: str
    phase_id: str
    is_completed: bool


# ─────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────

@router.get("/test")
async def test_endpoint():
    return JSONResponse(status_code=200, content={"status": "working"})

@router.get("")
async def get_all_roadmaps():
    """
    GET /roadmaps
    Returns all career paths (without phases, for listing/dropdown).
    """
    try:
        svc = get_roadmap_service()
        roadmaps = svc.get_all_roadmaps()
        data = []
        for r in roadmaps:
            data.append({
                "id": str(r.id),
                "career_name": r.name,
                "description": r.description,
                "estimated_duration": "N/A",
                "icon_name": "work",
                "created_at": None,
            })
        return JSONResponse(status_code=200, content={"roadmaps": data, "total": len(data)})
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return JSONResponse(status_code=200, content={"error": str(e), "traceback": tb})


@router.get("/recommendations/{user_id}")
async def get_recommended_roadmap(user_id: str):
    """
    GET /roadmaps/recommendations/{user_id}
    Returns a personalized roadmap recommendation based on skill gaps and preferences.
    """
    try:
        svc = get_roadmap_service()
        result = svc.get_recommended_roadmap(user_id)
        roadmap = result["roadmap"]
        if not roadmap:
            return JSONResponse(
                status_code=404,
                content={"detail": "No roadmaps found in database."}
            )
        # Get progress for this user
        completed_ids = svc.get_user_phase_progress(user_id, roadmap.id)
        return JSONResponse(
            status_code=200,
            content={
                "roadmap": _serialize_roadmap(roadmap, completed_ids),
                "reason": result["reason"],
                "highlighted_skills": result["highlighted_skills"],
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@router.get("/progress/{user_id}/{roadmap_id}")
async def get_user_roadmap_progress(user_id: str, roadmap_id: str):
    """
    GET /roadmaps/progress/{user_id}/{roadmap_id}
    Returns list of completed phase IDs for a user+roadmap.
    """
    try:
        svc = get_roadmap_service()
        completed_ids = svc.get_user_phase_progress(user_id, int(roadmap_id))
        return JSONResponse(
            status_code=200,
            content={
                "user_id": user_id,
                "roadmap_id": roadmap_id,
                "completed_phase_ids": [str(c) for c in completed_ids],
                "completed_count": len(completed_ids),
            }
        )
    except ValueError:
        return JSONResponse(status_code=400, content={"detail": "Invalid roadmap ID format"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@router.post("/progress/{user_id}")
async def update_phase_progress(user_id: str, request: PhaseProgressRequest):
    """
    POST /roadmaps/progress/{user_id}
    Mark or unmark a phase as completed.
    """
    try:
        svc = get_roadmap_service()
        success = svc.set_phase_completion(
            user_id=user_id,
            phase_id=int(request.phase_id),
            is_completed=request.is_completed,
        )
        return JSONResponse(
            status_code=200,
            content={
                "success": success,
                "user_id": user_id,
                "roadmap_id": request.roadmap_id,
                "phase_id": request.phase_id,
                "is_completed": request.is_completed,
            }
        )
    except ValueError:
        return JSONResponse(status_code=400, content={"detail": "Invalid phase ID format"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@router.get("/{roadmap_id}")
async def get_roadmap_by_id(roadmap_id: str):
    """
    GET /roadmaps/{roadmap_id}
    Returns a single roadmap with all phases.
    """
    try:
        svc = get_roadmap_service()
        roadmap = svc.get_roadmap_by_id(int(roadmap_id))
        if not roadmap:
            return JSONResponse(status_code=404, content={"detail": "Roadmap not found"})
        return JSONResponse(
            status_code=200,
            content={"roadmap": _serialize_roadmap(roadmap)}
        )
    except ValueError:
        return JSONResponse(status_code=400, content={"detail": "Invalid roadmap ID format"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
