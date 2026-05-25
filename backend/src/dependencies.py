from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.core.config import settings
from src.models import Validator, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/verify-otp")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_from_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        id: str = payload.get("id")
        role: str = payload.get("role")
        if id is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return {"id": id, "role": role}

def get_current_validator(current_user: dict = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    if current_user.get("role") != "validator" and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if current_user.get("role") == "admin":
        return {"id": "admin", "role": "admin", "name": "Admin"}

    validator = db.query(Validator).filter(Validator.id == current_user.get("id")).first()
    if not validator:
        raise HTTPException(status_code=404, detail="Validator not found")
    return validator

def get_current_user(current_user: dict = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    if current_user.get("role") != "user":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = db.query(User).filter(User.id == current_user.get("id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
