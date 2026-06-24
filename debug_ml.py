import sys
import traceback
from app.services.ml_service import get_ml_service
from app.api.ml_router import JobMatchRequest

try:
    ml_service = get_ml_service()
    res = ml_service.match_job(
        resume_score=0.8,
        skills_match_score=80.0,
        experience_years=2,
        education_level="Bachelor",
        industry="IT",
        job_market_demand="High"
    )
    with open("debug_out.txt", "w") as f:
        f.write(str(res))
except Exception as e:
    with open("debug_out.txt", "w") as f:
        f.write(traceback.format_exc())
