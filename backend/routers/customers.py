"""
Customer segmentation and RFM endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from pydantic import BaseModel
from backend.database import get_db

router = APIRouter()

# Pydantic models
class RFMCustomer(BaseModel):
    customerid: str
    recency: int
    frequency: int
    monetary: float
    r_score: int
    f_score: int
    m_score: int
    rfm_score: int
    segment: str

class SegmentSummary(BaseModel):
    segment: str
    customer_count: int
    total_revenue: float
    avg_monetary: float
    customer_percentage: float
    revenue_percentage: float

class CustomerValue(BaseModel):
    customerid: str
    total_spent: float
    total_orders: int
    avg_order_value: float
    days_since_last_order: int
    segment: str

@router.get("/segments", response_model=List[SegmentSummary])
async def get_segment_summary(
    db: Session = Depends(get_db)
):
    """Get summary of all customer segments"""
    
    query = text("""
        SELECT 
            segment,
            customer_count,
            total_revenue,
            avg_monetary,
            customer_percentage,
            revenue_percentage
        FROM segment_summary
        ORDER BY total_revenue DESC
    """)
    
    results = db.execute(query).fetchall()
    
    return [
        SegmentSummary(
            segment=row[0],
            customer_count=row[1],
            total_revenue=float(row[2]),
            avg_monetary=float(row[3]),
            customer_percentage=float(row[4]),
            revenue_percentage=float(row[5])
        ) for row in results
    ]

@router.get("/rfm/top", response_model=List[RFMCustomer])
async def get_top_customers(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get top customers by RFM score"""
    
    query = text("""
        SELECT 
            customerid,
            recency,
            frequency,
            monetary,
            r_score,
            f_score,
            m_score,
            rfm_score,
            segment
        FROM rfm_segments
        ORDER BY rfm_score DESC, monetary DESC
        LIMIT :limit
    """)
    
    results = db.execute(query, {"limit": limit}).fetchall()
    
    return [
        RFMCustomer(
            customerid=row[0],
            recency=row[1],
            frequency=row[2],
            monetary=float(row[3]),
            r_score=row[4],
            f_score=row[5],
            m_score=row[6],
            rfm_score=row[7],
            segment=row[8]
        ) for row in results
    ]

@router.get("/rfm/at-risk", response_model=List[RFMCustomer])
async def get_at_risk_customers(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get at-risk customers (need attention)"""
    
    query = text("""
        SELECT 
            customerid,
            recency,
            frequency,
            monetary,
            r_score,
            f_score,
            m_score,
            rfm_score,
            segment
        FROM rfm_segments
        WHERE segment LIKE '%At Risk%' OR segment LIKE '%Lost%'
        ORDER BY monetary DESC
        LIMIT :limit
    """)
    
    results = db.execute(query, {"limit": limit}).fetchall()
    
    return [
        RFMCustomer(
            customerid=row[0],
            recency=row[1],
            frequency=row[2],
            monetary=float(row[3]),
            r_score=row[4],
            f_score=row[5],
            m_score=row[6],
            rfm_score=row[7],
            segment=row[8]
        ) for row in results
    ]

@router.get("/rfm/champions", response_model=List[RFMCustomer])
async def get_champion_customers(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get champion customers (best customers)"""
    
    query = text("""
        SELECT 
            customerid,
            recency,
            frequency,
            monetary,
            r_score,
            f_score,
            m_score,
            rfm_score,
            segment
        FROM rfm_segments
        WHERE segment LIKE '%Champion%'
        ORDER BY monetary DESC
        LIMIT :limit
    """)
    
    results = db.execute(query, {"limit": limit}).fetchall()
    
    return [
        RFMCustomer(
            customerid=row[0],
            recency=row[1],
            frequency=row[2],
            monetary=float(row[3]),
            r_score=row[4],
            f_score=row[5],
            m_score=row[6],
            rfm_score=row[7],
            segment=row[8]
        ) for row in results
    ]

@router.get("/rfm/{customer_id}", response_model=CustomerValue)
async def get_customer_details(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific customer"""
    
    query = text("""
        SELECT 
            r.customerid,
            r.monetary as total_spent,
            r.frequency as total_orders,
            r.monetary / NULLIF(r.frequency, 0) as avg_order_value,
            r.recency as days_since_last_order,
            r.segment
        FROM rfm_segments r
        WHERE r.customerid = :customer_id
    """)
    
    result = db.execute(query, {"customer_id": customer_id}).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return CustomerValue(
        customerid=result[0],
        total_spent=float(result[1]),
        total_orders=result[2],
        avg_order_value=float(result[3]) if result[3] else 0,
        days_since_last_order=result[4],
        segment=result[5]
    )

@router.get("/rfm/stats/overview")
async def get_rfm_statistics(
    db: Session = Depends(get_db)
):
    """Get overall RFM statistics"""
    
    query = text("""
        SELECT 
            COUNT(*) as total_customers,
            AVG(recency) as avg_recency,
            AVG(frequency) as avg_frequency,
            AVG(monetary) as avg_monetary,
            SUM(monetary) as total_customer_value,
            MIN(recency) as best_recency,
            MAX(recency) as worst_recency,
            MAX(frequency) as max_frequency,
            MAX(monetary) as max_monetary
        FROM rfm_segments
    """)
    
    result = db.execute(query).first()
    
    return {
        "total_customers": result[0],
        "average_recency_days": round(float(result[1]), 1),
        "average_frequency": round(float(result[2]), 2),
        "average_customer_value": round(float(result[3]), 2),
        "total_customer_value": round(float(result[4]), 2),
        "best_recency_days": result[5],
        "worst_recency_days": result[6],
        "max_frequency": result[7],
        "max_customer_value": round(float(result[8]), 2)
    }