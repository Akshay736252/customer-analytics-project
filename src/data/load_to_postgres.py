import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'customer_analytics',
    'user': 'postgres',
    'password': 'YourNewPassword123'  # CHANGE THIS to your actual PostgreSQL password
}

def get_engine():
    connection_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return create_engine(connection_string)

def load_sales_data(engine):
    print("\n📊 Loading Sales Data...")
    try:
        df = pd.read_csv('data/processed/online_retail_enhanced.csv')
        df.to_sql('sales_data', engine, if_exists='replace', index=False, chunksize=10000)
        print(f"✅ Loaded {len(df):,} rows")
        return len(df)
    except Exception as e:
        print(f"❌ Error loading sales data: {e}")
        return 0

def load_rfm_data(engine):
    print("\n📊 Loading RFM Segments...")
    try:
        df = pd.read_csv('data/processed/rfm_segments.csv')
        df.to_sql('rfm_segments', engine, if_exists='replace', index=False)
        print(f"✅ Loaded {len(df):,} rows")
        return len(df)
    except Exception as e:
        print(f"❌ Error loading RFM data: {e}")
        return 0

def load_segment_summary(engine):
    print("\n📊 Loading Segment Summary...")
    try:
        df = pd.read_csv('data/processed/segment_summary.csv')
        df.to_sql('segment_summary', engine, if_exists='replace', index=False)
        print(f"✅ Loaded {len(df)} rows")
        return len(df)
    except Exception as e:
        print(f"❌ Error loading segment summary: {e}")
        return 0

def load_forecast_data(engine):
    print("\n📊 Loading Forecast Data...")
    try:
        df = pd.read_csv('data/processed/sales_forecast.csv')
        df.to_sql('sales_forecast', engine, if_exists='replace', index=False)
        print(f"✅ Loaded {len(df)} rows")
        return len(df)
    except Exception as e:
        print(f"❌ Error loading forecast data: {e}")
        return 0

def load_monthly_forecast(engine):
    print("\n📊 Loading Monthly Forecast...")
    try:
        df = pd.read_csv('data/processed/monthly_forecast.csv')
        df.to_sql('monthly_forecast', engine, if_exists='replace', index=False)
        print(f"✅ Loaded {len(df)} rows")
        return len(df)
    except Exception as e:
        print(f"❌ Error loading monthly forecast: {e}")
        return 0

def check_csv_files():
    """Check if all required CSV files exist"""
    files = [
        'data/processed/online_retail_enhanced.csv',
        'data/processed/rfm_segments.csv',
        'data/processed/segment_summary.csv',
        'data/processed/sales_forecast.csv',
        'data/processed/monthly_forecast.csv'
    ]
    
    print("\n📁 Checking CSV files...")
    all_exist = True
    for file in files:
        try:
            with open(file, 'r'):
                print(f"✅ Found: {file}")
        except FileNotFoundError:
            print(f"❌ Missing: {file}")
            all_exist = False
    
    return all_exist

def main():
    print("="*60)
    print("🚀 LOADING DATA TO POSTGRESQL")
    print("="*60)
    
    # First check if CSV files exist
    if not check_csv_files():
        print("\n❌ Please make sure all CSV files exist in data/processed/")
        print("Run your notebooks first to generate the CSV files.")
        return
    
    try:
        # Create engine
        engine = get_engine()
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("\n✅ Connected to PostgreSQL successfully")
        
        # Load all data
        total_rows = 0
        total_rows += load_sales_data(engine)
        total_rows += load_rfm_data(engine)
        total_rows += load_segment_summary(engine)
        total_rows += load_forecast_data(engine)
        total_rows += load_monthly_forecast(engine)
        
        print("\n" + "="*60)
        print(f"✅ SUCCESS! Loaded {total_rows:,} total rows")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your password in DB_CONFIG")
        print("3. Make sure database 'customer_analytics' exists")
        print("4. Try: net start postgresql-x64-16 (if PostgreSQL is stopped)")

if __name__ == "__main__":
    main()