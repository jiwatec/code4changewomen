from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from datetime import datetime
import uuid

from src.dependencies import get_current_volunteer, get_db
from src.schemas import VolunteerResponse, Token, LoginRequest, CertificationResponse, CertificationCreate
from src.core.security import get_password_hash, verify_password, create_access_token
from src.services.storage_service import upload_file_to_cloud

router = APIRouter(prefix="/api/volunteers", tags=["volunteers"])

@router.post("/register", response_model=VolunteerResponse)
def register_volunteer(
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    collegeProof: UploadFile = File(...),
    livePhoto: UploadFile = File(...),
    db = Depends(get_db)
):
    # Check uniqueness
    email_docs = db.collection('volunteers').where('email', '==', email).limit(1).get()
    if email_docs:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    phone_docs = db.collection('volunteers').where('phone', '==', phone).limit(1).get()
    if phone_docs:
        raise HTTPException(status_code=400, detail="Phone already registered")

    volunteer_id = str(uuid.uuid4())
    volunteer_code = f"VOL-{str(uuid.uuid4())[:8].upper()}"
    
    college_proof_url = upload_file_to_cloud(collegeProof, "proofs")
    live_photo_url = upload_file_to_cloud(livePhoto, "photos")

    volunteer = {
        "id": volunteer_id,
        "volunteerCode": volunteer_code,
        "email": email,
        "phone": phone,
        "passwordHash": get_password_hash(password),
        "collegeProofUrl": college_proof_url,
        "livePhotoUrl": live_photo_url,
        "isApproved": False,
        "createdAt": datetime.utcnow()
    }
    
    db.collection('volunteers').document(volunteer_id).set(volunteer)
    return volunteer

@router.post("/login", response_model=Token)
def login_volunteer(login_data: LoginRequest, db = Depends(get_db)):
    docs = db.collection('volunteers').where('email', '==', login_data.email).limit(1).get()
    if not docs:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    volunteer = docs[0].to_dict()
    if not verify_password(login_data.password, volunteer.get('passwordHash')):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not volunteer.get('isApproved', False):
        raise HTTPException(status_code=403, detail="Account not approved yet")
    
    access_token = create_access_token(data={"id": volunteer.get('id'), "role": "volunteer"})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/certifications", response_model=CertificationResponse)
def add_certification(
    title: str = Form(...),
    hoursValue: int = Form(...),
    proof: UploadFile = File(None),
    db = Depends(get_db),
    current_volunteer: dict = Depends(get_current_volunteer)
):
    cert_id = str(uuid.uuid4())
    cert_code = f"CERT-{str(uuid.uuid4())[:8].upper()}"
    proof_url = upload_file_to_cloud(proof, "certs") if proof else None

    cert = {
        "id": cert_id,
        "certCode": cert_code,
        "title": title,
        "hoursValue": hoursValue,
        "proofUrl": proof_url,
        "volunteerId": current_volunteer.get('id'),
        "issuedAt": datetime.utcnow()
    }
    db.collection('certifications').document(cert_id).set(cert)
    return cert

@router.get("/dashboard")
def get_dashboard(db = Depends(get_db), current_volunteer: dict = Depends(get_current_volunteer)):
    docs = db.collection('certifications').where('volunteerId', '==', current_volunteer.get('id')).get()
    certs = [doc.to_dict() for doc in docs]
    
    return {
        "volunteer": current_volunteer,
        "certifications": certs,
        "total_hours": sum(c.get('hoursValue', 0) for c in certs)
    }
