"""
Main FastAPI application for Customer Analytics System
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import os
from datetime import datetime

# Import routers (we'll create these next)
from backend.routers import sales, customers, forecast, auth

# Create FastAPI app
app = FastAPI(
    title="Customer Analytics API",
    description="REST API for Customer Behavior Analytics and Sales Forecasting",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sales.router, prefix="/api/sales", tags=["Sales"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["Forecast"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Customer Analytics API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "api": "operational"
        }
    }

# Run with: uvicorn backend.main:app --reload