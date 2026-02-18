"""
Sales data endpoints - FINAL FIX with correct column names
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from datetime import datetime, date
from backend.database import get_db

router = APIRouter()

@router.get("/test")
async def test_connection(db: Session = Depends(get_db)):
    """Simple test endpoint"""
    try:
        result = db.execute(text("SELECT 1")).first()
        
        # Get actual column names from the table
        columns = db.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name = 'sales_data'")
        ).fetchall()
        
        column_list = [col[0] for col in columns]
        
        return {
            "status": "connected",
            "test_query": result[0],
            "columns_in_table": column_list
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/summary")
async def get_sales_summary(db: Session = Depends(get_db)):
    """Get sales summary - with CORRECT column names"""
    try:
        # First, let's check what columns actually exist
        columns_check = db.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name = 'sales_data'")
        ).fetchall()
        
        column_names = [col[0] for col in columns_check]
        
        # Based on the error, the column is "TotalRevenue" (capital T and R)
        # Let's use the correct case
        query = text("""
            SELECT 
                SUM("TotalRevenue") as total_revenue,
                COUNT(DISTINCT "InvoiceNo") as total_orders,
                COUNT(DISTINCT "CustomerID") as unique_customers
            FROM sales_data
        """)
        
        result = db.execute(query).first()
        
        if not result:
            return {
                "total_revenue": 0,
                "total_orders": 0,
                "unique_customers": 0,
                "avg_order_value": 0,
                "columns_found": column_names
            }
        
        total_revenue = float(result[0]) if result[0] else 0
        total_orders = int(result[1]) if result[1] else 0
        unique_customers = int(result[2]) if result[2] else 0
        
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        return {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "unique_customers": unique_customers,
            "avg_order_value": round(avg_order_value, 2),
            "columns_found": column_names
        }
        
    except Exception as e:
        # If error, let's get the actual columns to help debug
        try:
            columns = db.execute(
                text("SELECT column_name FROM information_schema.columns WHERE table_name = 'sales_data'")
            ).fetchall()
            column_list = [col[0] for col in columns]
        except:
            column_list = ["Could not fetch columns"]
            
        return {
            "error": str(e),
            "error_type": str(type(e)),
            "columns_in_table": column_list,
            "total_revenue": 0,
            "total_orders": 0,
            "unique_customers": 0,
            "avg_order_value": 0
        }

@router.get("/columns")
async def get_table_columns(db: Session = Depends(get_db)):
    """Get all columns in sales_data table with their correct names"""
    try:
        query = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'sales_data'
            ORDER BY ordinal_position
        """)
        
        results = db.execute(query).fetchall()
        
        return {
            "table": "sales_data",
            "columns": [{"name": row[0], "type": row[1]} for row in results]
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/sample")
async def get_sample_data(db: Session = Depends(get_db)):
    """Get a sample row to see actual column names"""
    try:
        query = text("SELECT * FROM sales_data LIMIT 1")
        result = db.execute(query).first()
        
        if result:
            # Get column names from the result
            column_names = result._fields if hasattr(result, '_fields') else list(result.keys())
            return {
                "sample_row_exists": True,
                "column_names": column_names,
                "sample_data": dict(zip(column_names, result))
            }
        else:
            return {"sample_row_exists": False, "message": "No data in table"}
    except Exception as e:
        return {"error": str(e)}