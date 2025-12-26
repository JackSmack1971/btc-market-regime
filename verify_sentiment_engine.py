import time
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from src.streaming.sentiment_manager import SentimentStreamManager

def verify_sentiment_manager():
    print("Initializing SentimentStreamManager...")
    config = {"primary": "https://api.alternative.me/fng/"}
    manager = SentimentStreamManager(config)
    
    print("Starting manager...")
    manager.start()
    
    # Wait for data ingestion
    print("Waiting 10 seconds for initial sentiment tick...")
    time.sleep(10)
    
    latest = manager.get_latest()
    if latest:
        print(f"PASS: Retrieved latest sentiment: {latest.value} at {latest.timestamp}")
    else:
        print("FAIL: No sentiment data populated.")
        
    manager.stop()
    print("Manager stopped.")

if __name__ == "__main__":
    verify_sentiment_manager()
