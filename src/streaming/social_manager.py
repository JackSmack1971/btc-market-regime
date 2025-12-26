import threading
import time
import random
from collections import deque
from datetime import datetime
from typing import List, Dict, Any
from ..utils import logger

class SocialStreamManager:
    """Ingests social sentiment data asynchronously into a Conflation Queue."""
    
    def __init__(self, maxlen: int = 20):
        self.queue = deque(maxlen=maxlen)
        self._stop_event = threading.Event()
        self._thread = None
        self._lock = threading.Lock()
        
        # Mock data for demonstration (Twitter/Discord Bridge)
        self._mock_authors = ["@crypto_whale", "@btc_alchemist", "@macro_scout", "@chain_watcher", "@alpha_leak"]
        self._mock_templates = [
            "BTC breaking structural resistance at 98k. Volume confirms.",
            "Heavy spot buying on Coinbase. Institutional accumulation continues.",
            "MVRV Z-Score hitting overbought territory. Expecting mean reversion.",
            "Whale moved 5k BTC to cold storage. Bullish supply shock incoming.",
            "Sentiment pivot: Fear & Greed shifting to Extreme Greed. Caution advised."
        ]

    def start(self):
        """Starts the background ingestion thread."""
        if self._thread is not None:
            return
        
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_ingestion, daemon=True)
        self._thread.start()
        logger.info("SocialStreamManager started background thread")

    def stop(self):
        """Stops the background ingestion thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _run_ingestion(self):
        """Background loop to poll social data."""
        while not self._stop_event.is_set():
            try:
                # Simulate polling delay
                time.sleep(random.uniform(2, 5))
                
                # Create mock message
                msg = {
                    "id": random.randint(1000, 9999),
                    "author": random.choice(self._mock_authors),
                    "text": random.choice(self._mock_templates),
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "score": random.choice(["BULLISH", "BEARISH", "NEUTRAL"])
                }
                
                with self._lock:
                    self.queue.appendleft(msg)
                    
            except Exception as e:
                logger.error("Social ingestion error", error=str(e))
                time.sleep(1)

    def get_latest(self, count: int = 5) -> List[Dict[str, Any]]:
        """Returns the latest N messages from the queue."""
        with self._lock:
            return list(self.queue)[:count]
