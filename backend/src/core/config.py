import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    DIRECT_URL: str = ""
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    
    @property
    def sqlalchemy_url(self) -> str:
        return self.DATABASE_URL.replace("?pgbouncer=true", "").replace("&pgbouncer=true", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week
    
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "123456")

    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    class Config:
        env_file = ".env"

settings = Settings()
