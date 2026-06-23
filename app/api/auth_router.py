"""
Auth Router - Simple email authentication
"""
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from app.database.service import get_db_service
from app.database.models import UserProfile

router = APIRouter(prefix="/auth", tags=["Auth"])


class AuthSignupRequest(BaseModel):
    email: str
    password: str
    name: str = ""


class AuthLoginRequest(BaseModel):
    email: str
    password: str


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _issue_access_token(user_id: str, email: str) -> str:
    secret = os.getenv("AUTH_SECRET", "career_lens_dev_secret_change_me")
    now = int(datetime.now(timezone.utc).timestamp())
    nonce = secrets.token_hex(8)
    raw = f"{user_id}:{email}:{now}:{nonce}"
    sig = hmac.new(secret.encode("utf-8"), raw.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{raw}:{sig}"


@router.post("/signup")
def signup(request: AuthSignupRequest):
    """Create an account and return auth token."""
    email = _normalize_email(request.email)
    if not email:
        return JSONResponse(status_code=400, content={"detail": "Email is required"})

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
                "name": user.name or "User",
            },
        },
    )


@router.post("/login")
def login(request: AuthLoginRequest):
    """Authenticate and return token."""
    email = _normalize_email(request.email)
    if not email:
        return JSONResponse(status_code=400, content={"detail": "Email is required"})

    db_service = get_db_service()
    db = db_service.get_session()
    try:
        user = db.query(UserProfile).filter(UserProfile.email == email).first()
        if not user:
            # For testing/dev convenience, create profile if it doesn't exist
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
            },
        },
    )
