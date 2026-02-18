"""
Authentication endpoints (simplified version)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from backend.database import get_db

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

# For demo purposes, we'll use a simple token
@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Simple login endpoint"""
    
    # For demo, accept any credentials
    # In production, you'd validate against database
    return {
        "access_token": "demo-token-12345",
        "token_type": "bearer"
    }

@router.get("/me", response_model=User)
async def get_current_user(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False))
):
    """Get current user info"""
    
    # For demo, return a default user
    return User(
        username="demo_user",
        email="demo@example.com",
        full_name="Demo User",
        role="analyst"
    )

@router.get("/verify")
async def verify_token(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False))
):
    """Verify if token is valid"""
    return {"valid": True, "user": "demo_user"}