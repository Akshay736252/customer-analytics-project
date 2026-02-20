"""
Super Simple FastAPI App
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Customer Analytics API",
        "status": "working",
        "time": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/test")
async def test():
    return {"test": "successful"}

@app.get("/api/sales/summary")
async def sales_summary():
    return {
        "total_revenue": 1250000,
        "total_orders": 15000,
        "unique_customers": 5000,
        "avg_order_value": 83.33,
        "message": "Sample data - Database connection not required"
    }