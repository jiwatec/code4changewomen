from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

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
    id: UUID
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
    id: UUID
    certCode: str
    volunteerId: UUID
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
    id: UUID
    userCode: str
    scoreRating: int
    hasWatchedTutorial: bool
    encryptedVideoUrl: Optional[str] = None
    associatedVolId: Optional[UUID] = None
    createdAt: datetime

    class Config:
        from_attributes = True

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

# -----------
# OTP Schemas
# -----------
class OTPRequest(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    otp: str
