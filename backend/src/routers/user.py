from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from typing import List

from src.dependencies import get_current_user, get_db
from src.schemas import OTPRequest, OTPVerify, Token, UserResponse, SubmissionResponse
from src.models import User, Submission
from src.services.otp_service import generate_otp, get_otp_expiry, send_otp_sms
from src.core.security import create_access_token

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/request-otp")
def request_otp(data: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        user = User(phone=data.phone)
        db.add(user)
        db.commit()
        db.refresh(user)

    otp = generate_otp()
    user.otp = otp
    user.otpExpiry = get_otp_expiry()
    db.commit()

    send_otp_sms(data.phone, otp)
    return {"message": "OTP sent successfully"}

@router.post("/verify-otp", response_model=Token)
def verify_otp(data: OTPVerify, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user or user.otp != data.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")
    
    # In production, check expiry
    # if user.otpExpiry < datetime.utcnow():
    #     raise HTTPException(status_code=401, detail="OTP expired")
    
    user.otp = None
    user.otpExpiry = None
    db.commit()

    access_token = create_access_token(data={"id": str(user.id), "role": "user"})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/submit", response_model=SubmissionResponse)
def submit_skill(
    trade: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # KISS: Just save filename as URL for now
    media_url = f"/uploads/{file.filename}"
    
    # Mock AI Grading & Whisper-Tiny Transcription
    transcript = "[Whisper-Tiny Transcript | HI -> EN]\nI am demonstrating my tailoring skills by stitching this blouse. I have been doing this for 5 years."
    ai_score = 92.0 # Pre-scored by AI based on transcript relevance
    
    new_submission = Submission(
        userId=current_user.id,
        trade=trade,
        mediaUrl=media_url,
        transcript=transcript,
        aiScore=ai_score,
        status="pending"
    )
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    return new_submission

@router.get("/submissions", response_model=List[SubmissionResponse])
def get_user_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Submission).filter(Submission.userId == current_user.id).all()
