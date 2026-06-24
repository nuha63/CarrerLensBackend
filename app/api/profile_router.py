from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request
from sqlalchemy.orm import Session
import os
import uuid
from app.database.service import get_db_service
from app.database.models import UserProfile

router = APIRouter()

UPLOAD_DIR = "uploads/profile_pictures"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def get_db():
    db = get_db_service().get_session()
    try:
        yield db
    finally:
        db.close()

def validate_image(file: UploadFile) -> str:
    # Check extension
    filename = file.filename
    if not filename or "." not in filename:
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File must be a JPG, JPEG, or PNG")
    
    # Check mime type
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid MIME type")
        
    return ext

@router.post("/upload-photo/{user_id}")
async def upload_profile_photo(
    request: Request,
    user_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Verify user exists
    user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate file
    ext = validate_image(file)
    
    # Read file content to check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")
        
    # Generate unique secure filename
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    
    # Delete old file if it exists and is local
    if user.profile_image_url:
        old_filename = user.profile_image_url.split("/")[-1]
        old_path = os.path.join(UPLOAD_DIR, old_filename)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass
                
    # Save new file
    with open(file_path, "wb") as f:
        f.write(content)
        
    # Build full URL based on request base URL
    base_url = str(request.base_url).rstrip("/")
    image_url = f"{base_url}/{UPLOAD_DIR}/{new_filename}"
    
    # Update database
    user.profile_image_url = image_url
    db.commit()
    
    return {
        "success": True,
        "image_url": image_url
    }

@router.get("/photo/{user_id}")
def get_profile_photo(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not user.profile_image_url:
        raise HTTPException(status_code=404, detail="Profile photo not found")
        
    return {
        "image_url": user.profile_image_url
    }

@router.delete("/photo/{user_id}")
def delete_profile_photo(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not user.profile_image_url:
        return {"success": True}
        
    # Delete local file
    filename = user.profile_image_url.split("/")[-1]
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass
            
    # Update DB
    user.profile_image_url = None
    db.commit()
    
    return {"success": True}
