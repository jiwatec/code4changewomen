from fastapi import APIRouter, Depends, HTTPException
from src.dependencies import get_db
<<<<<<< HEAD
from src.schemas import CertificationPublicResponse
from src.services.qr_service import generate_qr_code_base64

router = APIRouter(prefix="/api/public", tags=["public"])

@router.get("/certificates/{certCode}", response_model=CertificationPublicResponse)
def get_certificate(certCode: str, db = Depends(get_db)):
    docs = db.collection('certifications').where('certCode', '==', certCode).limit(1).get()
    if not docs:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    cert_dict = docs[0].to_dict()
    
    volunteer_doc = db.collection('volunteers').document(cert_dict.get('volunteerId')).get()
    volunteer_name = None
    if volunteer_doc.exists:
        volunteer_name = volunteer_doc.to_dict().get('email')

    response = CertificationPublicResponse(**cert_dict)
    response.volunteer_name = volunteer_name
    return response

@router.get("/certificates/{certCode}/qr")
def get_certificate_qr(certCode: str, db = Depends(get_db)):
    docs = db.collection('certifications').where('certCode', '==', certCode).limit(1).get()
    if not docs:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    verification_url = f"https://frontend.com/verify/{certCode}"
    qr_base64 = generate_qr_code_base64(verification_url)
    return {"qr_code": qr_base64}
=======
from src.models import Certificate, User, Submission
from src.schemas import CertificateResponse

router = APIRouter(prefix="/api/public", tags=["public"])

@router.get("/verify/{cert_code}")
def verify_certificate(cert_code: str, db: Session = Depends(get_db)):
    cert = db.query(Certificate).filter(Certificate.certCode == cert_code).first()
    if not cert:
        # Try by hash
        cert = db.query(Certificate).filter(Certificate.hash == cert_code).first()
    
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    user = db.query(User).filter(User.id == cert.userId).first()
    submission = db.query(Submission).filter(Submission.id == cert.submissionId).first()
    
    return {
        "status": "valid",
        "certificate": {
            "code": cert.certCode,
            "hash": cert.hash,
            "issuedAt": cert.issuedAt,
            "skillScore": cert.skillScore,
            "professionalismScore": cert.professionalismScore
        },
        "artisan": {
            "phone": user.phone,
            "trade": submission.trade
        }
    }
>>>>>>> 1ecf60759c5880687b136805db2655f3eda0febb
