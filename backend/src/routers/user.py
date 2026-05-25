<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timezone
=======
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
>>>>>>> 1ecf60759c5880687b136805db2655f3eda0febb
import uuid
from typing import List

from src.dependencies import get_current_user, get_db
<<<<<<< HEAD
from src.schemas import OTPRequest, OTPVerify, Token, UserResponse
=======
from src.schemas import OTPRequest, OTPVerify, Token, UserResponse, SubmissionResponse
from src.models import User, Submission
>>>>>>> 1ecf60759c5880687b136805db2655f3eda0febb
from src.services.otp_service import generate_otp, get_otp_expiry, send_otp_sms
from src.core.security import create_access_token

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/request-otp")
<<<<<<< HEAD
def request_otp(data: OTPRequest, db = Depends(get_db)):
    docs = db.collection('users').where('phone', '==', data.phone).limit(1).get()
    
    if not docs:
        user_id = str(uuid.uuid4())
        user_code = f"USR-{str(uuid.uuid4())[:8].upper()}"
        user = {
            "id": user_id,
            "phone": data.phone,
            "userCode": user_code,
            "scoreRating": 0,
            "hasWatchedTutorial": False,
            "createdAt": datetime.utcnow()
        }
        db.collection('users').document(user_id).set(user)
    else:
        user = docs[0].to_dict()
        user_id = user.get('id')
=======
def request_otp(data: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        user = User(phone=data.phone)
        db.add(user)
        db.commit()
        db.refresh(user)
>>>>>>> 1ecf60759c5880687b136805db2655f3eda0febb

    otp = generate_otp()
    otp_expiry = get_otp_expiry()
    
    db.collection('users').document(user_id).update({
        "otp": otp,
        "otpExpiry": otp_expiry
    })

    send_otp_sms(data.phone, otp)
    return {"message": "OTP sent successfully"}

@router.post("/verify-otp", response_model=Token)
def verify_otp(data: OTPVerify, db = Depends(get_db)):
    docs = db.collection('users').where('phone', '==', data.phone).limit(1).get()
    if not docs:
        raise HTTPException(status_code=401, detail="Invalid OTP")
<<<<<<< HEAD
        
    user = docs[0].to_dict()
    if user.get('otp') != data.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")
        
    otp_expiry = user.get('otpExpiry')
    if otp_expiry:
        # Convert datetime.utcnow() to timezone-aware if otp_expiry is timezone-aware
        now = datetime.now(timezone.utc) if otp_expiry.tzinfo else datetime.utcnow()
        if otp_expiry < now:
            raise HTTPException(status_code=401, detail="OTP expired")
    
    # Clear OTP
    db.collection('users').document(user.get('id')).update({
        "otp": None,
        "otpExpiry": None
    })
=======
    
    # In production, check expiry
    # if user.otpExpiry < datetime.utcnow():
    #     raise HTTPException(status_code=401, detail="OTP expired")
    
    user.otp = None
    user.otpExpiry = None
    db.commit()
>>>>>>> 1ecf60759c5880687b136805db2655f3eda0febb

    access_token = create_access_token(data={"id": str(user.get('id')), "role": "user"})
    return {"access_token": access_token, "token_type": "bearer"}

<<<<<<< HEAD
@router.post("/tutorial-complete")
def complete_tutorial(db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db.collection('users').document(current_user.get('id')).update({
        "hasWatchedTutorial": True
    })
    return {"message": "Tutorial marked as completed"}

=======
>>>>>>> 1ecf60759c5880687b136805db2655f3eda0febb
@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: dict = Depends(get_current_user)):
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
