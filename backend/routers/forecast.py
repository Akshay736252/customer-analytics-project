"""
Sales forecast endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from backend.database import get_db

router = APIRouter()

# Pydantic models
class ForecastDay(BaseModel):
    date: str
    predicted_revenue: float
    confidence_lower: float
    confidence_upper: float
    month: str

class MonthlyForecast(BaseModel):
    month: str
    predicted_revenue: float

class ForecastSummary(BaseModel):
    total_forecast: float
    avg_daily: float
    peak_day: str
    peak_value: float
    low_day: str
    low_value: float
    days_forecasted: int

@router.get("/daily", response_model=List[ForecastDay])
async def get_daily_forecast(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get daily sales forecast"""
    
    query = text("""
        SELECT 
            TO_CHAR(forecast_date, 'YYYY-MM-DD') as date,
            predicted_revenue,
            confidence_lower,
            confidence_upper,
            month
        FROM sales_forecast
        ORDER BY forecast_date
        LIMIT :days
    """)
    
    results = db.execute(query, {"days": days}).fetchall()
    
    return [
        ForecastDay(
            date=row[0],
            predicted_revenue=float(row[1]),
            confidence_lower=float(row[2]),
            confidence_upper=float(row[3]),
            month=row[4]
        ) for row in results
    ]

@router.get("/monthly", response_model=List[MonthlyForecast])
async def get_monthly_forecast(
    db: Session = Depends(get_db)
):
    """Get monthly sales forecast"""
    
    query = text("""
        SELECT 
            forecast_month,
            predicted_revenue
        FROM monthly_forecast
        ORDER BY forecast_month
    """)
    
    results = db.execute(query).fetchall()
    
    return [
        MonthlyForecast(
            month=row[0],
            predicted_revenue=float(row[1])
        ) for row in results
    ]

@router.get("/summary", response_model=ForecastSummary)
async def get_forecast_summary(
    db: Session = Depends(get_db)
):
    """Get summary of sales forecast"""
    
    query = text("""
        SELECT 
            SUM(predicted_revenue) as total,
            AVG(predicted_revenue) as avg_daily,
            MAX(predicted_revenue) as peak,
            MIN(predicted_revenue) as low,
            COUNT(*) as days
        FROM sales_forecast
    """)
    
    result = db.execute(query).first()
    
    # Get peak and low dates
    peak_query = text("""
        SELECT 
            TO_CHAR(forecast_date, 'YYYY-MM-DD')
        FROM sales_forecast
        WHERE predicted_revenue = (SELECT MAX(predicted_revenue) FROM sales_forecast)
        LIMIT 1
    """)
    
    low_query = text("""
        SELECT 
            TO_CHAR(forecast_date, 'YYYY-MM-DD')
        FROM sales_forecast
        WHERE predicted_revenue = (SELECT MIN(predicted_revenue) FROM sales_forecast)
        LIMIT 1
    """)
    
    peak_date = db.execute(peak_query).scalar()
    low_date = db.execute(low_query).scalar()
    
    return ForecastSummary(
        total_forecast=float(result[0]),
        avg_daily=float(result[1]),
        peak_day=peak_date,
        peak_value=float(result[2]),
        low_day=low_date,
        low_value=float(result[3]),
        days_forecasted=result[4]
    )

@router.get("/insights")
async def get_forecast_insights(
    db: Session = Depends(get_db)
):
    """Get business insights from forecast"""
    
    # Get forecast data
    forecast_query = text("""
        SELECT 
            SUM(predicted_revenue) as total_90day,
            AVG(predicted_revenue) as avg_daily_forecast
        FROM sales_forecast
    """)
    
    # Get historical data for comparison
    historical_query = text("""
        SELECT 
            AVG(daily_revenue) as avg_daily_historical
        FROM daily_sales
        WHERE sale_date >= CURRENT_DATE - INTERVAL '90 days'
    """)
    
    forecast_result = db.execute(forecast_query).first()
    historical_result = db.execute(historical_query).first()
    
    forecast_avg = float(forecast_result[1])
    historical_avg = float(historical_result[0]) if historical_result[0] else 0
    
    # Calculate growth
    if historical_avg > 0:
        growth = ((forecast_avg - historical_avg) / historical_avg) * 100
    else:
        growth = 0
    
    # Get peak month
    month_query = text("""
        SELECT 
            forecast_month,
            predicted_revenue
        FROM monthly_forecast
        ORDER BY predicted_revenue DESC
        LIMIT 1
    """)
    
    peak_month = db.execute(month_query).first()
    
    return {
        "total_forecast_next_90days": round(float(forecast_result[0]), 2),
        "average_daily_forecast": round(forecast_avg, 2),
        "average_daily_historical": round(historical_avg, 2),
        "expected_growth_percentage": round(growth, 1),
        "peak_month": peak_month[0] if peak_month else None,
        "peak_month_revenue": round(float(peak_month[1]), 2) if peak_month else None,
        "recommendations": [
            f"Increase inventory by {max(0, round(growth))}% to meet expected demand",
            f"Prepare for peak season in {peak_month[0] if peak_month else 'upcoming months'}",
            "Plan promotions during low periods to boost sales",
            "Ensure adequate staffing for predicted busy periods"
        ]
    }