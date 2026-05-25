from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import uuid

from src.dependencies import get_current_volunteer, get_db
from src.schemas import VolunteerResponse, Token, LoginRequest, CertificationResponse, CertificationCreate
from src.models import Volunteer, Certification
from src.core.security import get_password_hash, verify_password, create_access_token
from src.dependencies import get_current_volunteer
from src.services.storage_service import upload_file_to_cloud

router = APIRouter(prefix="/api/volunteers", tags=["volunteers"])

@router.post("/register", response_model=VolunteerResponse)
def register_volunteer(
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    collegeProof: UploadFile = File(...),
    livePhoto: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if db.query(Volunteer).filter(Volunteer.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(Volunteer).filter(Volunteer.phone == phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")

    volunteer_code = f"VOL-{str(uuid.uuid4())[:8].upper()}"
    college_proof_url = upload_file_to_cloud(collegeProof, "proofs")
    live_photo_url = upload_file_to_cloud(livePhoto, "photos")

    new_volunteer = Volunteer(
        volunteerCode=volunteer_code,
        email=email,
        phone=phone,
        passwordHash=get_password_hash(password),
        collegeProofUrl=college_proof_url,
        livePhotoUrl=live_photo_url
    )
    db.add(new_volunteer)
    db.commit()
    db.refresh(new_volunteer)
    return new_volunteer

@router.post("/login", response_model=Token)
def login_volunteer(login_data: LoginRequest, db: Session = Depends(get_db)):
    volunteer = db.query(Volunteer).filter(Volunteer.email == login_data.email).first()
    if not volunteer or not verify_password(login_data.password, volunteer.passwordHash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not volunteer.isApproved:
        raise HTTPException(status_code=403, detail="Account not approved yet")
    
    access_token = create_access_token(data={"id": str(volunteer.id), "role": "volunteer"})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/certifications", response_model=CertificationResponse)
def add_certification(
    title: str = Form(...),
    hoursValue: int = Form(...),
    proof: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_volunteer: Volunteer = Depends(get_current_volunteer)
):
    cert_code = f"CERT-{str(uuid.uuid4())[:8].upper()}"
    proof_url = upload_file_to_cloud(proof, "certs") if proof else None

    new_cert = Certification(
        certCode=cert_code,
        title=title,
        hoursValue=hoursValue,
        proofUrl=proof_url,
        volunteerId=current_volunteer.id
    )
    db.add(new_cert)
    db.commit()
    db.refresh(new_cert)
    return new_cert

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), current_volunteer: Volunteer = Depends(get_current_volunteer)):
    certs = db.query(Certification).filter(Certification.volunteerId == current_volunteer.id).all()
    return {
        "volunteer": current_volunteer,
        "certifications": certs,
        "total_hours": sum(c.hoursValue for c in certs)
    }
