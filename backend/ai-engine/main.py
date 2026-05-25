import os
import torch
import base64
import urllib.parse
import json
import shutil
import datetime
import enum
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from transformers import pipeline
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Enum as SqlEnum, DateTime, ForeignKey, Text

# Pydantic Schemas
class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    model: str = Field(..., example="whisper-tiny")
    device: str = Field(..., example="cpu")
    supported_keywords: List[str]

class TranscriptionResponse(BaseModel):
    filename: str
    transcription: str

class GradingResponse(BaseModel):
    filename: str
    transcription: str
    translated_transcription: str
    keywords_found: List[str]
    confidence_score: float
    assessment_id: Optional[int] = Field(None, description="The ID of the saved assessment entry in the database.")
    status: Optional[str] = Field(None, description="Assessment grading status (approved, pending).")

class GovernmentScheme(BaseModel):
    id: int
    name: str
    description: str
    benefits: List[str]
    eligibility: str
    apply_link: str

class SchemesResponse(BaseModel):
    user_id: int
    certificate_detected: bool
    status_message: str
    schemes: List[GovernmentScheme]

# Database Setup & Schema
Base = declarative_base()

class UserRole(str, enum.Enum):
    admin = "admin"
    normal_user = "normal_user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SqlEnum(UserRole), default=UserRole.normal_user, nullable=False)
    
    certifications = Column(Text, nullable=True) 
    area = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    skill = Column(String, nullable=True)

class AssessmentStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    ipfs_cid = Column(String, nullable=True)
    media_type = Column(String, nullable=True)
    status = Column(SqlEnum(AssessmentStatus), default=AssessmentStatus.pending, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    transcript = Column(Text, nullable=True)
    ai_score = Column(Integer, nullable=True)

# Database URL extraction and base64url decoding
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = None
AsyncSessionLocal = None

if not DATABASE_URL:
    # Use SQLite as a fallback for local development
    DATABASE_URL = "sqlite+aiosqlite:///./rpl_platform.db"

if DATABASE_URL:
    # Decode prisma+postgres base64url connection URL
    if DATABASE_URL.startswith("prisma+postgres://"):
        try:
            parsed = urllib.parse.urlparse(DATABASE_URL)
            query_params = urllib.parse.parse_qs(parsed.query)
            api_key = query_params.get("api_key", [None])[0]
            if api_key:
                missing_padding = len(api_key) % 4
                padd = "=" * (4 - missing_padding) if missing_padding else ""
                decoded_payload = base64.urlsafe_b64decode(api_key + padd).decode("utf-8")
                payload = json.loads(decoded_payload)
                real_db_url = payload.get("databaseUrl")
                if real_db_url:
                    DATABASE_URL = real_db_url
        except Exception as e:
            print(f"Error decoding prisma+postgres URL: {e}")
            
    # Swap driver in URL for SQLAlchemy's psycopg dialect (100% compatible with local Prisma dev database!)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

    # Bypass IPv6 localhost DNS resolution latency/hangs
    if "localhost" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("localhost", "127.0.0.1")

    # Strip query parameters to prevent query parsing issues
    if "?" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.split("?")[0]

    # Initialize Async SQLAlchemy Engine
    engine_args = {}
    if DATABASE_URL.startswith("postgresql"):
        engine_args = {
            "pool_size": 20, 
            "max_overflow": 100,
            "connect_args": {"sslmode": "disable"}
        }

    engine = create_async_engine(
        DATABASE_URL, 
        echo=False,
        **engine_args
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine, 
        class_=AsyncSession, 
        expire_on_commit=False,
        autocommit=False, 
        autoflush=False
    )

async def get_db():
    if AsyncSessionLocal is None:
        raise HTTPException(
            status_code=500,
            detail="Database is not configured. Please set the DATABASE_URL environment variable."
        )
    async with AsyncSessionLocal() as session:
        yield session

# Lifespan context manager for startup and shutdown actions
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables using the async engine
    if engine is not None:
        print("Connecting to database and creating tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables initialized successfully!")
    yield
    # Shutdown: Close database connections
    if engine is not None:
        await engine.dispose()
        print("Database connections closed.")

app = FastAPI(
    title="AI Engine - Unified ML Model & Grading Services",
    description="FastAPI service utilizing Whisper-Tiny to grade speaking assessments and manage Neon database scheme integrations.",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model Initialization
print("Initializing Whisper-Tiny pipeline...")
device = "cuda:0" if torch.cuda.is_available() else "cpu"
transcriber = pipeline(
    "automatic-speech-recognition", 
    model="openai/whisper-tiny", 
    device=device
)
print(f"Model loaded successfully on device: {device}")

# Multilingual mapping for the 15 core tailoring keywords
# Maps each keyword to its English, transliterated, and native Hindi/Kannada representations
KEYWORDS_MAPPING = {
    "bobbin": ["bobbin", "bobin", "babin", "bambin", "बोबिन", "ಬಾಬಿನ್"],
    "seam": ["seam", "seem", "sima", "seema", "सीम", "ಸೀಮ್"],
    "stitch": ["stitch", "silai", "tanka", "holige", "holigay", "सिलाई", "टांका", "ಹೊಲಿಗೆ"],
    "needle": ["needle", "sui", "suji", "sooji", "सुई", "ಸೂಜಿ"],
    "fabric": ["fabric", "kapada", "kapda", "kapade", "kapparay", "batte", "bhatte", "bhattimattu", "कपड़ा", "कपड़े", "ಬಟ್ಟೆ"],
    "measure": ["measure", "map", "nap", "maap", "naap", "mahap", "alate", "alata", "माಪ್", "ಮಾಪ್", "माप", "नाप", "ಅಳತೆ"],
    "hemming": ["hemming", "hemin", "himin", "heming", "turpai", "तूरपाई", "ಹೆಮ್ಮಿಂಗ್"],
    "pattern": ["pattern", "patan", "patran", "vinyasa", "पैटर्न", "ವಿನ್ಯಾಸ"],
    "tailor": ["tailor", "darji", "dharji", "darjee", "दर्जी", "ದರ್ಜಿ"],
    "cut": ["cut", "katna", "kata", "katar", "kattari", "काटना", "कतरना", "ಕತ್ತರಿಸು"],
    "blouse": ["blouse", "choli", "kanchala", "चोली", "ಬ್ಲೌಸ್"],
    "thread": ["thread", "dhaga", "dhaaga", "daaga", "noolu", "धागा", "ದಾರ"],
    "sewing machine": ["machine", "silai machine", "mishin", "yantra", "सिलाई मशीन", "ಯಂತ್ರ"],
    "lining": ["lining", "astar", "स्तर", "ಲೈನಿಂಗ್"],
    "pleats": ["pleats", "plate", "chunnat", "चुन्नट", "ಪ್ಲೀಟ್ಸ್"]
}

# Higher weight for technical terms vs general terms
KEYWORD_WEIGHTS = {
    "bobbin": 1.5,
    "seam": 1.5,
    "hemming": 1.5,
    "lining": 1.5,
    "pleats": 1.5,
    "pattern": 1.2,
    "measure": 1.2,
    "stitch": 1.0,
    "needle": 1.0,
    "fabric": 1.0,
    "cut": 1.0,
    "thread": 0.8,
    "blouse": 0.8,
    "tailor": 0.5,
    "sewing machine": 0.5
}

@app.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "healthy",
        "model": "whisper-tiny",
        "device": device,
        "supported_keywords": list(KEYWORDS_MAPPING.keys())
    }

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: Optional[UploadFile] = File(None, description="The audio file to transcribe (mp3, wav, m4a, webm, etc.)"),
    language: Optional[str] = Form(
        None, 
        description="Select spoken language: 'hi' (Hindi), 'kn' (Kannada), 'en' (English). If left blank, Whisper auto-detects it."
    )
):
    if file is None:
        raise HTTPException(
            status_code=400,
            detail="No file uploaded. Please upload a valid audio file under the 'file' form field."
        )
        
    temp_file = f"temp_{file.filename}"
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Build generation kwargs
        gen_kwargs = {}
        if language and language.strip().lower() in ["hi", "kn", "en"]:
            gen_kwargs["language"] = language.strip().lower()
            
        result = transcriber(temp_file, generate_kwargs=gen_kwargs)
        
        return {
            "filename": file.filename,
            "transcription": result.get("text", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

@app.post("/grade_assessment", response_model=GradingResponse)
async def grade_assessment(
    file: Optional[UploadFile] = File(None, description="The audio file to grade (mp3, wav, m4a, webm, etc.)"),
    language: Optional[str] = Form(
        None, 
        description="Select spoken language: 'hi' (Hindi), 'kn' (Kannada), 'en' (English). If left blank, Whisper auto-detects it."
    ),
    user_id: Optional[int] = Form(
        None,
        description="Optional user ID to link and save this assessment score in the database."
    ),
    ipfs_cid: Optional[str] = Form(
        None,
        description="Optional IPFS CID of the assessment file to save in the database."
    ),
    db: Optional[AsyncSession] = Depends(get_db)
):
    if file is None:
        raise HTTPException(
            status_code=400,
            detail="No file uploaded. Please upload a valid audio file under the 'file' form field."
        )
        
    # Verify user exists if user_id is supplied
    if user_id is not None:
        if db is None:
            raise HTTPException(
                status_code=500,
                detail="Database session is not available. Please verify DATABASE_URL configuration."
            )
        from sqlalchemy import select
        user_result = await db.execute(select(User).filter(User.id == user_id))
        user = user_result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} was not found in the database. Please register the user first."
            )
        
    temp_file = f"temp_{file.filename}"
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Build generation kwargs
        gen_kwargs = {}
        if language and language.strip().lower() in ["hi", "kn", "en"]:
            gen_kwargs["language"] = language.strip().lower()
            
        # 1. Generate Transcription (Highly stable, handles mixed/native languages)
        transcription_res = transcriber(temp_file, generate_kwargs={"task": "transcribe", **gen_kwargs})
        raw_text = transcription_res.get("text", "")
        
        # 2. Generate Translation to English with high-quality settings
        translation_res = transcriber(
            temp_file, 
            generate_kwargs={
                "task": "translate",
                "repetition_penalty": 1.2,
                "no_repeat_ngram_size": 4,
                "num_beams": 5, # Beam Search for better translation
                **gen_kwargs
            }
        )
        translated_text = translation_res.get("text", "")
        
        # Combine both texts to maximize matches across scripts and languages
        combined_text_lower = (raw_text + " " + translated_text).lower()
        
        # Match keywords using mapping and calculate weighted score
        keywords_found = []
        weighted_score = 0.0
        max_possible_weight = sum(KEYWORD_WEIGHTS.values())
        
        for keyword_key, variants in KEYWORDS_MAPPING.items():
            found_this_keyword = False
            for variant in variants:
                if variant.lower() in combined_text_lower:
                    found_this_keyword = True
                    break
            
            if found_this_keyword:
                keywords_found.append(keyword_key)
                weighted_score += KEYWORD_WEIGHTS.get(keyword_key, 1.0)
                    
        # Calculate confidence score (0 to 100) normalized by weights
        confidence_score = round((weighted_score / max_possible_weight) * 100, 2)
        
        # Boost score slightly if they mentioned highly technical terms
        if any(kw in keywords_found for kw in ["bobbin", "seam", "hemming", "lining", "pleats"]):
            confidence_score = min(100.0, confidence_score * 1.1)
        
        status_val = AssessmentStatus.approved if confidence_score >= 40.0 else AssessmentStatus.pending
        
        assessment_id = None
        # Save to database if user_id is provided
        if user_id is not None:
            new_assessment = Assessment(
                user_id=user_id,
                ipfs_cid=ipfs_cid,
                media_type=file.content_type,
                status=status_val,
                transcript=raw_text,
                ai_score=int(confidence_score)
            )
            db.add(new_assessment)
            await db.commit()
            await db.refresh(new_assessment)
            assessment_id = new_assessment.id
        
        return {
            "filename": file.filename,
            "transcription": raw_text,
            "translated_transcription": translated_text,
            "keywords_found": keywords_found,
            "confidence_score": confidence_score,
            "assessment_id": assessment_id,
            "status": status_val.value if user_id is not None else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

@app.get("/get_jobs", response_model=SchemesResponse)
async def get_jobs(user_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Fetch user from database
    from sqlalchemy import select
    user_result = await db.execute(select(User).filter(User.id == user_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} was not found. Please register the user first to search for schemes."
        )
        
    # 2. Check if they have a valid certificate
    has_cert_field = user.certifications is not None and len(user.certifications.strip()) > 0
    
    # Check if they have an approved tailoring assessment
    assessment_result = await db.execute(
        select(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.status == AssessmentStatus.approved
        )
    )
    approved_assessment = assessment_result.scalars().first()
    has_approved_assessment = approved_assessment is not None
    
    is_certified = has_cert_field or has_approved_assessment
    
    # Curated tailoring government schemes
    ALL_SCHEMES = [
        {
            "id": 1,
            "name": "Pradhan Mantri Vishwakarma Yojana (PM-VY)",
            "description": "A comprehensive national scheme designed to provide collateral-free credit support, skill training, and toolkits for traditional tailors (Darjis) and artisans.",
            "benefits": [
                "Collateral-free loan of up to ₹3,00,000 at a highly concessional interest rate of 5%.",
                "Advanced tailoring toolkit incentive of ₹15,000.",
                "Stipend of ₹500/day during advanced skill training courses."
            ],
            "eligibility": "Certified traditional tailors and self-employed artisans aged 18+.",
            "apply_link": "https://pmvishwakarma.gov.in/"
        },
        {
            "id": 2,
            "name": "PM Mudra Scheme (Tailoring Enterprise Grant)",
            "description": "Government loan program offering Shishu and Kishor micro-loans to certified tailoring practitioners to establish full-scale tailoring boutiques and retail units.",
            "benefits": [
                "Shishu Loans up to ₹50,000 with 0% processing fees.",
                "Kishor Loans up to ₹5,00,000 for purchasing advanced double-needle industrial sewing machines.",
                "Flexible tenure ranging from 3 to 5 years."
            ],
            "eligibility": "Skilled tailors possessing a recognized assessment score or certificate.",
            "apply_link": "https://www.mudra.org.in/"
        },
        {
            "id": 3,
            "name": "Deendayal Antyodaya Yojana (DAY-NULM Tailor Co-operatives)",
            "description": "Supports urban and rural tailoring collectives and self-help groups (SHGs) by offering interest subvention loans and premium marketplace listings.",
            "benefits": [
                "Interest subvention of 7% on self-employment group tailoring loans.",
                "Free stalls at regional Saras Melas and national handicraft exhibitions.",
                "Direct raw material supply chains for fabrics and sewing kits."
            ],
            "eligibility": "Certified tailoring professionals who are members of registered self-help groups (SHGs).",
            "apply_link": "https://nulm.gov.in/"
        }
    ]
    
    if is_certified:
        return {
            "user_id": user_id,
            "certificate_detected": True,
            "status_message": "Congratulations! A valid skill certificate or approved prior learning assessment has been recognized. You have unlocked full access to premium government schemes and grants.",
            "schemes": ALL_SCHEMES
        }
    else:
        return {
            "user_id": user_id,
            "certificate_detected": False,
            "status_message": "Access Restricted. No active certificate or approved assessment found for your profile. Please complete your Hindi/Kannada speaking voice assessment with a score >= 50% to unlock these lucrative government benefits.",
            "schemes": []
        }

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="User's question or message")
    context: str = Field(default="general", description="Context for the chat (vocational_assessment_platform, general, etc.)")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI assistant's response")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level of the response")

# RPL Platform Knowledge Base
RPL_KNOWLEDGE_BASE = {
    "assessment": "An RPL (Recognition of Prior Learning) assessment evaluates your existing skills and knowledge through practical demonstrations like video submissions.",
    "certification": "Upon successful assessment, you receive a recognized vocational certificate that unlocks government schemes and financial benefits.",
    "prior_learning": "RPL recognizes skills you've acquired through work experience, informal training, and self-learning, not just formal education.",
    "skills": "We assess various vocational skills including tailoring, handicrafts, food preparation, beauty, domestic work, and manufacturing.",
    "government_schemes": "Once certified, you can access schemes like PM Vishwakarma Yojana, PM Mudra, and DAY-NULM for loans and financial support.",
    "process": "The process involves logging in, selecting your skill, uploading a video demonstration, waiting for AI assessment, and receiving certification.",
    "login": "Use the login page with your username and password. Demo credentials: test_artisan (artisan) or test_admin (validator).",
    "upload": "After login, go to the Hub page and submit a video or audio file demonstrating your skill in Hindi or Kannada.",
}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    AI Chat endpoint for answering questions about the RPL platform.
    Provides helpful responses to user queries about assessments, certifications, and government schemes.
    """
    query = request.query.lower().strip()
    confidence = 0.0
    response = ""
    
    # Simple keyword matching and knowledge base lookup
    for keyword, answer in RPL_KNOWLEDGE_BASE.items():
        if keyword in query:
            response = answer
            confidence = 0.9
            break
    
    # Default helpful responses for common patterns
    if not response:
        if any(word in query for word in ["how", "what", "where", "when", "why"]):
            if any(word in query for word in ["start", "begin", "get", "login"]):
                response = "To get started, visit the login page. Use demo credentials test_artisan for artisan access or test_admin for validator access. Then select your skill and upload your assessment video."
                confidence = 0.7
            elif any(word in query for word in ["benefit", "advantage", "money", "earn", "income"]):
                response = "Certified professionals unlock access to government schemes like PM Vishwakarma Yojana offering up to ₹3,00,000 in collateral-free loans, PM Mudra for microloans, and DAY-NULM co-operative support."
                confidence = 0.75
            elif any(word in query for word in ["skill", "assess", "video", "submit"]):
                response = "Submit a 2-5 minute video demonstrating your skill in Hindi or Kannada. Our AI system will analyze your video, transcribe your speech, and assess your skill level. You'll receive instant feedback and certification if you meet the requirements."
                confidence = 0.8
            else:
                response = "I'm here to help with questions about vocational assessments, certifications, government schemes, and the RPL platform. What would you like to know?"
                confidence = 0.5
        else:
            response = "I'm here to help! Ask me about RPL assessments, skill certifications, government schemes, or how to get started with the platform."
            confidence = 0.6
    
    return ChatResponse(response=response, confidence=confidence)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
