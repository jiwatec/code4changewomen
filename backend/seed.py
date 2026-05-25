<<<<<<< HEAD
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/c/Users/ASUS/Desktop/np/backend')

import uuid
from datetime import datetime

from src.database import db

try:
    # Create a test volunteer
    vol_id = str(uuid.uuid4())
    volunteer_code = f"VOL-{str(uuid.uuid4())[:8].upper()}"
    volunteer = {
        "id": vol_id,
        "volunteerCode": volunteer_code,
        "email": "volunteer@test.com",
        "phone": "+1234567890",
        "passwordHash": "$2b$12$dummy_hash_value_for_test",
        "collegeProofUrl": "https://example.com/proof.pdf",
        "livePhotoUrl": "https://example.com/photo.jpg",
        "isApproved": True,
        "createdAt": datetime.utcnow()
    }
    db.collection('volunteers').document(vol_id).set(volunteer)
    print(f"✅ Created volunteer: {volunteer_code}")

    # Create a test user
    user_id = str(uuid.uuid4())
    user_code = f"USR-{str(uuid.uuid4())[:8].upper()}"
    user = {
        "id": user_id,
        "userCode": user_code,
        "phone": "+9876543210",
        "scoreRating": 100,
        "hasWatchedTutorial": True,
        "createdAt": datetime.utcnow()
    }
    db.collection('users').document(user_id).set(user)
    print(f"✅ Created user: {user_code}")

    # Create a test certification
    cert_id = str(uuid.uuid4())
    cert_code = f"CERT-{str(uuid.uuid4())[:8].upper()}"
    cert = {
        "id": cert_id,
        "certCode": cert_code,
        "title": "Community Service Excellence",
        "hoursValue": 50,
        "proofUrl": "https://example.com/cert.pdf",
        "volunteerId": vol_id,
        "issuedAt": datetime.utcnow()
    }
    db.collection('certifications').document(cert_id).set(cert)
    print(f"✅ Created certification: {cert_code}")

    print("\n✅ Database seeded successfully!")
    print("Check Firebase console - you should now see data in your collections.")

except Exception as e:
    print(f"❌ Error: {e}")
=======
from src.database import SessionLocal
from src.models import Validator, Base
from src.database import engine
from src.core.security import get_password_hash

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if validator already exists
    if not db.query(Validator).filter(Validator.email == "validator@nss.org").first():
        validator = Validator(
            email="validator@nss.org",
            passwordHash=get_password_hash("password123"),
            name="NSS Official"
        )
        db.add(validator)
        db.commit()
        print("Seed: Validator created.")
    else:
        print("Seed: Validator already exists.")
    
    db.close()

if __name__ == "__main__":
    seed()
>>>>>>> 1ecf60759c5880687b136805db2655f3eda0febb
