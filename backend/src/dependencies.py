from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from src.database import db
from src.core.config import settings
<<<<<<< HEAD
=======
from src.models import Validator, User
>>>>>>> 1ecf60759c5880687b136805db2655f3eda0febb

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/verify-otp")

def get_db():
    try:
        yield db
    finally:
        pass

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

<<<<<<< HEAD
def get_current_volunteer(current_user: dict = Depends(get_current_user_from_token)):
    if current_user.get("role") != "volunteer":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    vol_doc = db.collection('volunteers').document(current_user.get("id")).get()
    if not vol_doc.exists:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    volunteer = vol_doc.to_dict()
    volunteer['id'] = vol_doc.id

    if not volunteer.get('isApproved'):
        raise HTTPException(status_code=403, detail="Volunteer is not approved yet")
    return volunteer
=======
    validator = db.query(Validator).filter(Validator.id == current_user.get("id")).first()
    if not validator:
        raise HTTPException(status_code=404, detail="Validator not found")
    return validator
>>>>>>> 1ecf60759c5880687b136805db2655f3eda0febb

def get_current_user(current_user: dict = Depends(get_current_user_from_token)):
    if current_user.get("role") != "user":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user_doc = db.collection('users').document(current_user.get("id")).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = user_doc.to_dict()
    user['id'] = user_doc.id
    return user
