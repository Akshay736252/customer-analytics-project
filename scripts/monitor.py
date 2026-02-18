"""
Simple monitoring script
"""

import requests
import time
from datetime import datetime

API_URL = "http://localhost:8000"
ENDPOINTS = [
    "/api/health",
    "/api/sales/summary",
    "/api/customers/rfm/stats/overview",
    "/api/forecast/summary"
]

def check_endpoint(url):
    try:
        start = time.time()
        response = requests.get(url)
        duration = time.time() - start
        
        return {
            "url": url,
            "status": response.status_code,
            "duration": round(duration * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "url": url,
            "status": "ERROR",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def monitor():
    print(f"\n📊 Monitoring at {datetime.now().isoformat()}")
    print("-" * 50)
    
    for endpoint in ENDPOINTS:
        result = check_endpoint(API_URL + endpoint)
        if result["status"] == 200:
            print(f"✅ {endpoint:30s} - {result['duration']}ms")
        else:
            print(f"❌ {endpoint:30s} - {result.get('error', result['status'])}")

if __name__ == "__main__":
    while True:
        monitor()
        time.sleep(60)  # Check every minute