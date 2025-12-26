import time
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from src.streaming.mvrv_manager import MVRVStreamManager

def verify_mvrv_manager():
    print("Initializing MVRVStreamManager...")
    config = {"primary": "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?metrics=CapMVRVCur&assets=btc"}
    manager = MVRVStreamManager(config)
    
    print("Starting manager...")
    manager.start()
    
    # Wait for data ingestion
    print("Waiting 10 seconds for initial MVRV tick...")
    time.sleep(10)
    
    latest = manager.get_latest()
    if latest:
        print(f"PASS: Retrieved latest MVRV: {latest.value} at {latest.timestamp}")
    else:
        print("FAIL: No MVRV data populated.")
        
    manager.stop()
    print("Manager stopped.")

if __name__ == "__main__":
    verify_mvrv_manager()
