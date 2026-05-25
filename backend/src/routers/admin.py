from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import hashlib
import uuid

<<<<<<< HEAD
from src.dependencies import get_current_admin, get_db
from src.schemas import AdminLoginRequest, Token, VolunteerResponse
from src.core.config import settings
from src.core.security import create_access_token
=======
from src.dependencies import get_current_validator, get_db
from src.schemas import AdminLoginRequest, Token, SubmissionResponse
from src.models import Submission, Certificate, User, Validator
from src.core.config import settings
from src.core.security import create_access_token, verify_password
>>>>>>> 1ecf60759c5880687b136805db2655f3eda0febb

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/login", response_model=Token)
def admin_login(login_data: AdminLoginRequest, db: Session = Depends(get_db)):
    # Check if it's super admin
    if login_data.username == settings.ADMIN_USERNAME and login_data.password == settings.ADMIN_PASSWORD:
        access_token = create_access_token(data={"id": "admin", "role": "admin"})
        return {"access_token": access_token, "token_type": "bearer"}
    
    # Check if it's a validator
    validator = db.query(Validator).filter(Validator.email == login_data.username).first()
    if validator and verify_password(login_data.password, validator.passwordHash):
        access_token = create_access_token(data={"id": str(validator.id), "role": "validator"})
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(status_code=401, detail="Incorrect username or password")

<<<<<<< HEAD
@router.get("/volunteers/pending", response_model=List[VolunteerResponse])
def get_pending_volunteers(db = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    docs = db.collection('volunteers').where('isApproved', '==', False).get()
    return [doc.to_dict() for doc in docs]

@router.put("/volunteers/{id}/approve")
def approve_volunteer(id: str, db = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    doc_ref = db.collection('volunteers').document(id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    doc_ref.update({"isApproved": True})
    return {"message": "Volunteer approved successfully"}
=======
@router.get("/submissions/pending", response_model=List[SubmissionResponse])
def get_pending_submissions(
    db: Session = Depends(get_db), 
    current_validator: dict = Depends(get_current_validator)
):
    submissions = db.query(Submission).filter(Submission.status == "pending").all()
    results = []
    for sub in submissions:
        user = db.query(User).filter(User.id == sub.userId).first()
        sub_dict = {
            "id": sub.id,
            "userId": sub.userId,
            "trade": sub.trade,
            "mediaUrl": sub.mediaUrl,
            "transcript": sub.transcript,
            "aiScore": sub.aiScore,
            "status": sub.status,
            "createdAt": sub.createdAt,
            "phone": user.phone if user else "Unknown"
        }
        results.append(sub_dict)
    return results

@router.post("/submissions/{id}/approve")
def approve_submission(
    id: str, 
    skillScore: float,
    professionalismScore: float,
    db: Session = Depends(get_db), 
    current_validator: dict = Depends(get_current_validator)
):
    submission = db.query(Submission).filter(Submission.id == id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    submission.status = "approved"
    
    # Generate Certificate
    cert_code = f"CERT-{str(uuid.uuid4())[:8].upper()}"
    payload = f"{submission.id}-{submission.transcript}-{cert_code}"
    # Keccak256 equivalent
    cert_hash = hashlib.sha3_256(payload.encode()).hexdigest()
    
    certificate = Certificate(
        userId=submission.userId,
        submissionId=submission.id,
        certCode=cert_code,
        hash=cert_hash,
        skillScore=skillScore,
        professionalismScore=professionalismScore
    )
    db.add(certificate)
    db.commit()
    
    return {"message": "Submission approved and certificate issued", "certificate_id": str(certificate.id)}

@router.post("/submissions/{id}/reject")
def reject_submission(
    id: str, 
    db: Session = Depends(get_db), 
    current_validator: dict = Depends(get_current_validator)
):
    submission = db.query(Submission).filter(Submission.id == id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    submission.status = "rejected"
    db.commit()
    return {"message": "Submission rejected"}
>>>>>>> 1ecf60759c5880687b136805db2655f3eda0febb
