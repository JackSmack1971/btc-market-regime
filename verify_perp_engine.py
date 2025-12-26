import time
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from src.streaming.perp_manager import PerpStreamManager

def verify_perp_manager():
    print("Initializing PerpStreamManager...")
    config = {"primary": "https://fapi.binance.com/fapi/v1/fundingRate"}
    manager = PerpStreamManager(config)
    
    print("Starting manager...")
    manager.start()
    
    # Wait for data ingestion
    print("Waiting 10 seconds for initial funding tick...")
    time.sleep(10)
    
    latest = manager.get_latest()
    if latest:
        print(f"PASS: Retrieved latest funding: {latest.value} at {latest.timestamp}")
    else:
        print("FAIL: No funding data populated.")
        
    manager.stop()
    print("Manager stopped.")

if __name__ == "__main__":
    verify_perp_manager()
