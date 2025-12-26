import time
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from src.streaming.social_manager import SocialStreamManager

def verify_manager():
    print("Initializing SocialStreamManager...")
    manager = SocialStreamManager(maxlen=5)
    
    print("Starting manager...")
    manager.start()
    
    # Wait for data ingestion
    print("Waiting 10 seconds for data to populate...")
    time.sleep(10)
    
    latest = manager.get_latest(5)
    print(f"Retrieved {len(latest)} messages.")
    
    for msg in latest:
        print(f"[{msg['timestamp']}] {msg['author']}: {msg['text'][:30]}... | {msg['score']}")
        
    if len(latest) > 0:
        print("PASS: SocialStreamManager populated queue successfully.")
    else:
        print("FAIL: No data populated in queue.")
        
    manager.stop()
    print("Manager stopped.")

if __name__ == "__main__":
    verify_manager()
