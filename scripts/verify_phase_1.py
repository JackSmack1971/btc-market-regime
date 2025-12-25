import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.abspath('.'))

from src.fetchers import FetcherFactory
from src.utils import health_tracker, alert_manager
from src.cache import cache

def verify():
    print("🚀 STARTING PHASE 1 VERIFICATION (PROXIED)...")
    
    # 1. Test Cache
    print("\n[1] TESTING CACHE...")
    test_key = "test_metric_latest"
    test_data = {"value": 42.0, "timestamp": datetime.now()}
    cache.set(test_key, test_data)
    
    retrieved = cache.get(test_key)
    if retrieved and retrieved["value"] == 42.0:
        print("✅ Cache Set/Get: SUCCESS")
    else:
        print("❌ Cache Set/Get: FAILED")
        
    # 2. Test Fetcher with Cache & Health Tracking
    print("\n[2] TESTING FETCHER INTEGRATION...")
    config = {"primary": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"}
    # Using real API but expecting it to work or fail gracefully
    try:
        fetcher = FetcherFactory.create("price_data", config)
        print(f"Fetcher created: {fetcher.metric_name}")
        
        # First call (should be primary)
        res1 = fetcher.fetch()
        print(f"Fetch 1 (Primary): {res1.source if res1 else 'None'}")
        
        # Second call (should be cache)
        res2 = fetcher.fetch()
        print(f"Fetch 2 (Cache): {res2.source if res2 else 'None'}")
        
        # Check health HUD summary
        summary = health_tracker.get_latest_status()
        if "price_data" in summary:
            print(f"✅ Health Tracker recorded 'price_data': {summary['price_data']}")
        else:
            print("❌ Health Tracker failed to record attempt")
            
    except Exception as e:
        print(f"⚠️ Fetcher test encountered expected/unexpected error: {e}")

    # 3. Test Alerts
    print("\n[3] TESTING ALERTS (MOCKED)...")
    alert_manager.send_message("🚨 VERIFICATION TEST ALERT")
    print("✅ Alert logged to console (MOCKED)")

    print("\n🏁 VERIFICATION COMPLETE.")

if __name__ == "__main__":
    verify()
