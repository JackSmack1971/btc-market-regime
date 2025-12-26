import time
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from src.streaming.flow_manager import FlowStreamManager

def verify_flow_manager():
    print("Initializing FlowStreamManager...")
    config = {"primary": "https://api.cryptoquant.com/v1/bitcoin/exchange-flows/netflow"}
    manager = FlowStreamManager(config)
    
    print("Starting manager...")
    manager.start()
    
    # Wait for data ingestion
    print("Waiting 10 seconds for initial flow tick...")
    time.sleep(10)
    
    latest = manager.get_latest()
    if latest:
        print(f"PASS: Retrieved latest flow: {latest.value} BTC at {latest.timestamp}")
    else:
        print("FAIL: No flow data populated.")
        
    manager.stop()
    print("Manager stopped.")

if __name__ == "__main__":
    verify_flow_manager()
