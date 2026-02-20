"""
Authentication endpoints - Simplified version
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()

# Simple token model
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: str
    full_name: str
    role: str

# Simple hardcoded users for demo
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "role": "admin",
        "password": "admin123"
    },
    "analyst": {
        "username": "analyst",
        "email": "analyst@example.com",
        "full_name": "Data Analyst",
        "role": "analyst",
        "password": "analyst123"
    }
}

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Simple login endpoint"""
    
    # Check if user exists
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return token (simplified)
    return {
        "access_token": f"token-{form_data.username}-{datetime.now().timestamp()}",
        "token_type": "bearer"
    }

@router.get("/me", response_model=User)
async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False))):
    """Get current user info"""
    
    # Simplified - return a default user
    return User(
        username="demo_user",
        email="demo@example.com",
        full_name="Demo User",
        role="analyst"
    )

@router.get("/verify")
async def verify_token():
    """Verify if token is valid"""
    return {"valid": True, "user": "demo_user"}