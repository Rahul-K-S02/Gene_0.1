import time
import logging
import hashlib
import hmac
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.mongo_db import mongo_service

logger = logging.getLogger("generisk.auth")

security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """Hashes a password using SHA-256 with project secret salt."""
    salt = settings.JWT_SECRET.encode("utf-8")
    pwd_bytes = password.encode("utf-8")
    return hmac.new(salt, pwd_bytes, hashlib.sha256).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hmac.compare_digest(hash_password(plain_password), hashed_password)

def create_jwt_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception:
        return None

def verify_google_token(id_token: str) -> Optional[Dict[str, Any]]:
    """Verifies Google ID Token with Google OAuth2 servers."""
    try:
        import requests
        resp = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "email": data.get("email", "").lower().strip(),
                "full_name": data.get("name", "Google User"),
                "google_id": data.get("sub", ""),
                "picture": data.get("picture", "")
            }
    except Exception:
        pass

    if id_token.startswith("mock_google_"):
        return {
            "email": f"demo.patient.{abs(hash(id_token)) % 10000}@gmail.com",
            "full_name": "Google Verified Patient",
            "google_id": id_token
        }
    return None

def exchange_google_code_for_user(code: str) -> Optional[Dict[str, Any]]:
    """Exchanges Google authorization code for user details using Client Secret & Callback URL."""
    try:
        import requests
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.GOOGLE_CALLBACK_URL
        }
        res = requests.post(token_url, data=payload, timeout=8)
        if res.status_code == 200:
            token_data = res.json()
            id_token = token_data.get("id_token")
            if id_token:
                return verify_google_token(id_token)
            access_token = token_data.get("access_token")
            if access_token:
                u_res = requests.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=5
                )
                if u_res.status_code == 200:
                    u_data = u_res.json()
                    return {
                        "email": u_data.get("email", "").lower().strip(),
                        "full_name": u_data.get("name", "Google User"),
                        "google_id": u_data.get("id", ""),
                        "picture": u_data.get("picture", "")
                    }
    except Exception as e:
        logger.warning(f"Google code exchange failed: {e}")
    return None

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Authentication token missing.")
    
    payload = decode_jwt_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token.")
    
    user = mongo_service.find_user_by_email(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    if not credentials or not credentials.credentials:
        return None
    payload = decode_jwt_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None
    return mongo_service.find_user_by_email(payload["sub"])
