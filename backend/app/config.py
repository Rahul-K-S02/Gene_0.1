import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseModel):
    PROJECT_NAME: str = "GeneRisk"
    VERSION: str = "2.0.0"
    API_PREFIX: str = "/api/v1"
    
    # MongoDB Atlas (Optional: Local persistent document store is used if omitted)
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "generisk_db")
    
    # JWT Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", "generisk-super-secret-jwt-key-2026")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 72
    
    # Google OAuth Credentials (from Google Cloud Console)
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_CALLBACK_URL: str = os.getenv("GOOGLE_CALLBACK_URL", "http://localhost:8000/api/v1/auth/google/callback")
    FRONTEND_REDIRECT_URL: str = os.getenv("FRONTEND_REDIRECT_URL", "http://localhost:3000")
    
    # Relational Database (Turso or local SQLite)
    TURSO_DATABASE_URL: str = os.getenv("TURSO_DATABASE_URL", "")
    TURSO_AUTH_TOKEN: str = os.getenv("TURSO_AUTH_TOKEN", "")
    LOCAL_DB_PATH: Path = BASE_DIR / "data" / "generisk.db"
    
    # Qdrant Vector DB (Cloud or local memory)
    # Existing collection 'major_project' preserved as requested
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "major_project")
    
    # NCBI PubMed E-utilities Configuration
    NCBI_EMAIL: str = os.getenv("NCBI_EMAIL", "generisk.research@gmail.com")
    NCBI_API_KEY: str = os.getenv("NCBI_API_KEY", "")
    PUBMED_SYNC_ENABLED: bool = os.getenv("PUBMED_SYNC_ENABLED", "true").lower() == "true"
    PUBMED_SYNC_MAX_AGE_DAYS: int = int(os.getenv("PUBMED_SYNC_MAX_AGE_DAYS", "7"))
    PUBMED_MAX_ARTICLES_PER_DISEASE: int = int(os.getenv("PUBMED_MAX_ARTICLES_PER_DISEASE", "20"))
    
    # Groq API & Fallback Models
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    GROQ_FALLBACK_MODELS: list[str] = [
        m.strip() for m in os.getenv(
            "GROQ_FALLBACK_MODELS",
            "llama-3.3-70b-versatile,llama-3.1-8b-instant,mixtral-8x7b-32768,gemma2-9b-it"
        ).split(",") if m.strip()
    ]
    
    # Model & Data directories
    MODELS_DIR: Path = BASE_DIR / "models"
    DATA_DIR: Path = BASE_DIR / "data"
    
    # CORS Origins
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.vercel.app",
    ]

settings = Settings()

# Ensure directories exist
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
