from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.dependencies import get_db
from src.models import Certification
from src.schemas import CertificationPublicResponse
from src.services.qr_service import generate_qr_code_base64

router = APIRouter(prefix="/api/public", tags=["public"])

@router.get("/certificates/{certCode}", response_model=CertificationPublicResponse)
def get_certificate(certCode: str, db: Session = Depends(get_db)):
    cert = db.query(Certification).filter(Certification.certCode == certCode).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    response = CertificationPublicResponse.model_validate(cert)
    response.volunteer_name = cert.volunteer.email  # Just sending email as an example
    return response

@router.get("/certificates/{certCode}/qr")
def get_certificate_qr(certCode: str, db: Session = Depends(get_db)):
    cert = db.query(Certification).filter(Certification.certCode == certCode).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    # Placeholder frontend URL
    verification_url = f"https://frontend.com/verify/{certCode}"
    qr_base64 = generate_qr_code_base64(verification_url)
    return {"qr_code": qr_base64}
