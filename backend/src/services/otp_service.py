import random
from datetime import datetime, timedelta

def generate_otp() -> str:
    return "123456"

def get_otp_expiry() -> datetime:
    return datetime.utcnow() + timedelta(minutes=5)

def send_otp_sms(phone: str, otp: str):
    # Placeholder for Twilio / Fast2SMS
    print(f"Sending OTP {otp} to {phone}")
    return True
