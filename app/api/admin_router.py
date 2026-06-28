from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.service import get_db_service
from app.database.models import UserProfile, UserProgress, ResumeAnalysis, Payment, JobMatch
from datetime import datetime, timezone
from pydantic import BaseModel

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])

# Dependencies
def get_db():
    db = get_db_service().get_session()
    try:
        yield db
    finally:
        db.close()

# Temporary dependency to check admin rights - in a real app this would use the auth token
def verify_admin(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

@router.get("/stats")
def get_dashboard_stats(user_id: str, db: Session = Depends(get_db)):
    verify_admin(user_id, db)
    
    total_users = db.query(UserProfile).count()
    premium_users = db.query(UserProfile).filter(UserProfile.is_premium == True).count()
    
    total_payments_amount = db.query(func.sum(Payment.amount)).filter(Payment.status == "approved").scalar() or 0.0
    
    resume_analyses_count = db.query(ResumeAnalysis).count()
    job_matches_count = db.query(JobMatch).count()
    
    # Get recent payment requests
    recent_payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(5).all()
    
    return {
        "total_users": total_users,
        "premium_users": premium_users,
        "total_revenue": total_payments_amount,
        "resume_analyses": resume_analyses_count,
        "job_matches": job_matches_count,
        "recent_payments": [
            {
                "id": p.payment_id,
                "user_id": p.user_id,
                "amount": p.amount,
                "status": p.status,
                "created_at": p.created_at
            } for p in recent_payments
        ]
    }

@router.get("/users")
def get_all_users(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    verify_admin(user_id, db)
    users = db.query(UserProfile).offset(skip).limit(limit).all()
    return [
        {
            "user_id": u.user_id,
            "email": u.email,
            "name": u.name,
            "is_premium": u.is_premium,
            "is_admin": u.is_admin,
            "created_at": u.created_at
        } for u in users
    ]

@router.get("/payments")
def get_all_payments(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    verify_admin(user_id, db)
    payments = db.query(Payment).order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": p.payment_id,
            "user_id": p.user_id,
            "amount": p.amount,
            "status": p.status,
            "method": p.payment_method,
            "created_at": p.created_at
        } for p in payments
    ]

class PaymentApprovalRequest(BaseModel):
    payment_id: str
    status: str  # 'approved' or 'rejected'

@router.post("/payments/approve")
def approve_payment(user_id: str, request: PaymentApprovalRequest, db: Session = Depends(get_db)):
    verify_admin(user_id, db)
    
    payment = db.query(Payment).filter(Payment.payment_id == request.payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
        
    payment.status = request.status
    payment.updated_at = datetime.now(timezone.utc)
    
    # If approved, grant premium to user
    if request.status == "approved":
        user = db.query(UserProfile).filter(UserProfile.user_id == payment.user_id).first()
        if user:
            user.is_premium = True
            # Example: 30 days premium
            from datetime import timedelta
            user.premium_expiry = datetime.now(timezone.utc) + timedelta(days=30)
            
    db.commit()
    return {"message": f"Payment {request.status} successfully"}

class PremiumRequest(BaseModel):
    user_id: str
    amount: float
    method: str
    transaction_id: str | None = None

@router.post("/payments/request")
def request_premium(request: PremiumRequest, db: Session = Depends(get_db)):
    # This is a public endpoint for users to submit a payment request
    payment = Payment(
        user_id=request.user_id,
        amount=request.amount,
        status="pending",
        payment_method=request.method,
        transaction_id=request.transaction_id
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return {"message": "Payment request submitted", "payment_id": payment.payment_id}
