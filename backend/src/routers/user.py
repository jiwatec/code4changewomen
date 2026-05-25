from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from src.dependencies import get_current_user, get_db
from src.schemas import OTPRequest, OTPVerify, Token, UserResponse
from src.models import User
from src.services.otp_service import generate_otp, get_otp_expiry, send_otp_sms
from src.core.security import create_access_token
from src.dependencies import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/request-otp")
def request_otp(data: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        user_code = f"USR-{str(uuid.uuid4())[:8].upper()}"
        user = User(phone=data.phone, userCode=user_code)
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
    if user.otpExpiry < datetime.utcnow():
        raise HTTPException(status_code=401, detail="OTP expired")
    
    # Clear OTP
    user.otp = None
    user.otpExpiry = None
    db.commit()

    access_token = create_access_token(data={"id": str(user.id), "role": "user"})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/tutorial-complete")
def complete_tutorial(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.hasWatchedTutorial = True
    db.commit()
    return {"message": "Tutorial marked as completed"}

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
