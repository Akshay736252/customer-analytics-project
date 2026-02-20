"""
Main FastAPI application for Customer Analytics System
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os

# Try to import routers, but don't fail if they're not available
try:
    from backend.routers import sales, customers, forecast, auth
    routers_available = True
except ImportError as e:
    print(f"Warning: Some routers could not be imported: {e}")
    routers_available = False

# Create FastAPI app
app = FastAPI(
    title="Customer Analytics API",
    description="Customer Behavior Analytics and Sales Forecasting System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers if available
if routers_available:
    try:
        app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
        app.include_router(sales.router, prefix="/api/sales", tags=["Sales"])
        app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
        app.include_router(forecast.router, prefix="/api/forecast", tags=["Forecast"])
        print("✅ All routers loaded successfully")
    except Exception as e:
        print(f"❌ Error loading routers: {e}")

@app.get("/")
async def root():
    return {
        "message": "Customer Analytics API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/api/docs",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("RENDER", "development")
    }

@app.get("/api/test")
async def test():
    """Simple test endpoint"""
    return {"message": "API is working!"}