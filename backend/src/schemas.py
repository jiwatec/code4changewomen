from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

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
    certificate: Optional['CertificateResponse'] = None

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
