import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, String, Integer, DateTime, ForeignKey
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Volunteer(Base):
    __tablename__ = "volunteers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    volunteerCode = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    passwordHash = Column(String, nullable=False)
    collegeProofUrl = Column(String, nullable=False)
    livePhotoUrl = Column(String, nullable=False)
    isApproved = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.utcnow)

    certifications = relationship("Certification", back_populates="volunteer", cascade="all, delete")
    usersAssigned = relationship("User", back_populates="associatedVolunteer")

class Certification(Base):
    __tablename__ = "certifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certCode = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    hoursValue = Column(Integer, nullable=False)
    proofUrl = Column(String, nullable=True)
    volunteerId = Column(UUID(as_uuid=True), ForeignKey("volunteers.id"), nullable=False)
    issuedAt = Column(DateTime, default=datetime.utcnow)

    volunteer = relationship("Volunteer", back_populates="certifications")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    userCode = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    otp = Column(String, nullable=True)
    otpExpiry = Column(DateTime, nullable=True)
    scoreRating = Column(Integer, default=0)
    hasWatchedTutorial = Column(Boolean, default=False)
    encryptedVideoUrl = Column(String, nullable=True)
    associatedVolId = Column(UUID(as_uuid=True), ForeignKey("volunteers.id"), nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)

    associatedVolunteer = relationship("Volunteer", back_populates="usersAssigned")
