import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, String, Integer, DateTime, ForeignKey, Float
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    trade = Column(String, nullable=True)
    otp = Column(String, nullable=True)
    otpExpiry = Column(DateTime, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)

    submissions = relationship("Submission", back_populates="user")
    certificates = relationship("Certificate", back_populates="user")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    userId = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    trade = Column(String, nullable=False)
    mediaUrl = Column(String, nullable=False)
    transcript = Column(String, nullable=True)
    aiScore = Column(Float, default=0.0)
    status = Column(String, default="pending") # pending, approved, rejected
    createdAt = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="submissions")
    certificate = relationship("Certificate", back_populates="submission", uselist=False)

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    userId = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    submissionId = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False)
    certCode = Column(String, unique=True, index=True, nullable=False)
    hash = Column(String, nullable=False)
    issuedAt = Column(DateTime, default=datetime.utcnow)
    skillScore = Column(Float, nullable=False)
    professionalismScore = Column(Float, nullable=False)

    user = relationship("User", back_populates="certificates")
    submission = relationship("Submission", back_populates="certificate")

class Validator(Base):
    __tablename__ = "validators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    passwordHash = Column(String, nullable=False)
    name = Column(String, nullable=False)
