from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.dependencies import get_current_admin, get_db
from src.schemas import AdminLoginRequest, Token, VolunteerResponse
from src.models import Volunteer
from src.core.config import settings
from src.core.security import create_access_token
from src.dependencies import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/login", response_model=Token)
def admin_login(login_data: AdminLoginRequest):
    if login_data.username == settings.ADMIN_USERNAME and login_data.password == settings.ADMIN_PASSWORD:
        access_token = create_access_token(data={"id": "admin_id", "role": "admin"})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")

@router.get("/volunteers/pending", response_model=List[VolunteerResponse])
def get_pending_volunteers(db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    volunteers = db.query(Volunteer).filter(Volunteer.isApproved == False).all()
    return volunteers

@router.put("/volunteers/{id}/approve")
def approve_volunteer(id: str, db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    volunteer = db.query(Volunteer).filter(Volunteer.id == id).first()
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    volunteer.isApproved = True
    db.commit()
    return {"message": "Volunteer approved successfully"}
