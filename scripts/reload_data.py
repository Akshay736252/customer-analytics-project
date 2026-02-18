"""
Complete data reload script - SQLAlchemy 2.0 compatible
Run this to refresh all data
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database configuration - UPDATED WITH YOUR PASSWORD
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'customer_analytics',
    'user': 'postgres',
    'password': 'YourNewPassword123'  # Your updated password
}

def get_engine():
    connection_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return create_engine(connection_string)

def reload_sales_data(engine):
    """Reload sales data from CSV"""
    print("\n📊 Reloading Sales Data...")
    df = pd.read_csv('data/processed/online_retail_enhanced.csv')
    
    # Ensure correct column names for database
    df.to_sql('sales_data', engine, if_exists='replace', index=False, chunksize=10000)
    print(f"✅ Loaded {len(df):,} rows")
    return len(df)

def reload_rfm_data(engine):
    """Reload RFM data"""
    print("\n📊 Reloading RFM Data...")
    df = pd.read_csv('data/processed/rfm_segments.csv')
    df.to_sql('rfm_segments', engine, if_exists='replace', index=False)
    print(f"✅ Loaded {len(df):,} rows")
    return len(df)

def recreate_daily_sales(engine):
    """Recreate daily sales from raw data"""
    print("\n📊 Recreating Daily Sales...")
    
    with engine.connect() as conn:
        # Drop table if exists
        conn.execute(text("DROP TABLE IF EXISTS daily_sales"))
        
        # Create daily_sales table
        query = """
        CREATE TABLE daily_sales AS
        SELECT 
            DATE("InvoiceDate") as sale_date,
            SUM("TotalRevenue") as daily_revenue,
            COUNT(DISTINCT "InvoiceNo") as transaction_count,
            AVG("TotalRevenue") as avg_order_value
        FROM sales_data
        GROUP BY DATE("InvoiceDate")
        ORDER BY sale_date;
        """
        
        conn.execute(text(query))
        conn.commit()
        
        # Verify
        result = conn.execute(text("SELECT COUNT(*) FROM daily_sales"))
        count = result.scalar()
        print(f"✅ Created daily_sales with {count} rows")
        return count

def recreate_country_summary(engine):
    """Recreate country summary"""
    print("\n📊 Recreating Country Summary...")
    
    with engine.connect() as conn:
        # Get total revenue
        result = conn.execute(text("SELECT SUM(\"TotalRevenue\") FROM sales_data"))
        total_revenue = result.scalar()
        
        # Drop table if exists
        conn.execute(text("DROP TABLE IF EXISTS country_summary"))
        
        query = f"""
        CREATE TABLE country_summary AS
        SELECT 
            "Country" as country,
            SUM("TotalRevenue") as total_revenue,
            COUNT(DISTINCT "InvoiceNo") as transaction_count,
            AVG("TotalRevenue") as avg_transaction_value,
            (SUM("TotalRevenue") * 100.0 / {total_revenue}) as revenue_share_percentage
        FROM sales_data
        GROUP BY "Country"
        ORDER BY total_revenue DESC;
        """
        
        conn.execute(text(query))
        conn.commit()
        
        # Verify
        result = conn.execute(text("SELECT COUNT(*) FROM country_summary"))
        count = result.scalar()
        print(f"✅ Created country_summary with {count} rows")
        return count

def recreate_product_summary(engine):
    """Recreate product summary"""
    print("\n📊 Recreating Product Summary...")
    
    with engine.connect() as conn:
        # Drop table if exists
        conn.execute(text("DROP TABLE IF EXISTS product_performance"))
        
        query = """
        CREATE TABLE product_performance AS
        SELECT 
            "Description" as description,
            SUM("Quantity") as total_quantity,
            SUM("TotalRevenue") as total_revenue,
            AVG("UnitPrice") as avg_unit_price
        FROM sales_data
        GROUP BY "Description"
        ORDER BY total_revenue DESC;
        """
        
        conn.execute(text(query))
        conn.commit()
        
        # Verify
        result = conn.execute(text("SELECT COUNT(*) FROM product_performance"))
        count = result.scalar()
        print(f"✅ Created product_performance with {count} rows")
        return count

def create_indexes(engine):
    """Create indexes for better performance"""
    print("\n📊 Creating Indexes...")
    
    with engine.connect() as conn:
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_sales_date ON sales_data(\"InvoiceDate\")",
            "CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales_data(\"CustomerID\")",
            "CREATE INDEX IF NOT EXISTS idx_sales_country ON sales_data(\"Country\")",
            "CREATE INDEX IF NOT EXISTS idx_rfm_customer ON rfm_segments(customerid)",
        ]
        
        for idx in indexes:
            try:
                conn.execute(text(idx))
                conn.commit()
                print(f"✅ Created index: {idx[:50]}...")
            except Exception as e:
                print(f"⚠️ Index error: {e}")
    
    print("✅ Indexes created")

def verify_data(engine):
    """Verify all tables have data"""
    print("\n" + "="*60)
    print("🔍 VERIFYING DATA")
    print("="*60)
    
    tables = ['sales_data', 'rfm_segments', 'daily_sales', 'country_summary', 'product_performance']
    
    with engine.connect() as conn:
        for table in tables:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"✅ {table:20s}: {count:10,} rows")
            except Exception as e:
                print(f"❌ {table:20s}: Error - {str(e)[:50]}")

def main():
    print("="*60)
    print("🔄 COMPLETE DATA RELOAD")
    print("="*60)
    
    start_time = datetime.now()
    
    try:
        engine = get_engine()
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Connected to database")
        
        # Reload all data
        reload_sales_data(engine)
        reload_rfm_data(engine)
        recreate_daily_sales(engine)
        recreate_country_summary(engine)
        recreate_product_summary(engine)
        create_indexes(engine)
        
        # Verify
        verify_data(engine)
        
        # Time taken
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "="*60)
        print(f"✅ DATA RELOAD COMPLETE in {duration:.1f} seconds")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()