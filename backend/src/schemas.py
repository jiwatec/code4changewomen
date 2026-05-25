from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
<<<<<<< HEAD
# -----------------
# Volunteer Schemas
# -----------------
class VolunteerBase(BaseModel):
    email: EmailStr
    phone: str

class VolunteerCreate(VolunteerBase):
    password: str
    # Note: files like collegeProof and livePhoto will be handled via Form/UploadFile in FastAPI routes,
    # so they aren't strictly part of the JSON payload schema.

class VolunteerResponse(VolunteerBase):
    id: str
    volunteerCode: str
    collegeProofUrl: str
    livePhotoUrl: str
    isApproved: bool
    createdAt: datetime

    class Config:
        from_attributes = True

# ---------------------
# Certification Schemas
# ---------------------
class CertificationBase(BaseModel):
    title: str
    hoursValue: int
    proofUrl: Optional[str] = None

class CertificationCreate(CertificationBase):
    pass

class CertificationResponse(CertificationBase):
    id: str
    certCode: str
    volunteerId: str
    issuedAt: datetime

    class Config:
        from_attributes = True

class CertificationPublicResponse(CertificationResponse):
    volunteer_name: Optional[str] = None # Added for public display optionally

# ------------
# User Schemas
# ------------
class UserBase(BaseModel):
    phone: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: str
    userCode: str
    scoreRating: int
    hasWatchedTutorial: bool
    encryptedVideoUrl: Optional[str] = None
    associatedVolId: Optional[str] = None
    createdAt: datetime

    class Config:
        from_attributes = True
=======
from uuid import UUID
>>>>>>> 1ecf60759c5880687b136805db2655f3eda0febb

# ------------
# Auth Schemas
# ------------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class OTPRequest(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    otp: str

# ------------
# User Schemas
# ------------
class UserBase(BaseModel):
    phone: str
    name: Optional[str] = None
    trade: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    createdAt: datetime

    class Config:
        from_attributes = True

# ------------------
# Submission Schemas
# ------------------
class SubmissionBase(BaseModel):
    trade: str
    mediaUrl: str
    transcript: Optional[str] = None
    aiScore: float = 0.0
    status: str = "pending"

class SubmissionResponse(SubmissionBase):
    id: UUID
    userId: UUID
    createdAt: datetime
    phone: Optional[str] = None

    class Config:
        from_attributes = True

# -------------------
# Certificate Schemas
# -------------------
class CertificateBase(BaseModel):
    certCode: str
    hash: str
    issuedAt: datetime
    skillScore: float
    professionalismScore: float

class CertificateResponse(CertificateBase):
    id: UUID
    userId: UUID
    submissionId: UUID

    class Config:
        from_attributes = True

# -----------------
# Validator Schemas
# -----------------
class ValidatorResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str

    class Config:
        from_attributes = True
