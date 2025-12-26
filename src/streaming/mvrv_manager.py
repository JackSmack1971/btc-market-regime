import threading
import time
import asyncio
import aiohttp
from collections import deque
from typing import Optional, Dict, Any
from ..fetchers.valuation import MVRVFetcher
from ..utils import logger

class MVRVStreamManager:
    """Async manager for MVRV Ratio with a Conflation Queue."""
    
    def __init__(self, config: Dict[str, Any]):
        self.fetcher = MVRVFetcher("mvrv_ratio", config)
        self.queue = deque(maxlen=1)
        self._stop_event = threading.Event()
        self._thread = None
        self._lock = threading.Lock()
        
    def start(self):
        """Starts the background polling thread."""
        if self._thread is not None:
            return
        
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("MVRVStreamManager started background thread")

    def stop(self):
        """Stops the background polling thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _run_loop(self):
        """Background loop using a private event loop for async fetching."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def poll():
            async with aiohttp.ClientSession() as session:
                while not self._stop_event.is_set():
                    try:
                        # Fetch latest MVRV tick
                        data = await self.fetcher.fetch(session)
                        if data:
                            with self._lock:
                                self.queue.append(data)
                        
                        # MVRV is a daily/hourly metric; poll every 5 minutes
                        for _ in range(300):
                            if self._stop_event.is_set():
                                break
                            await asyncio.sleep(1)
                            
                    except Exception as e:
                        logger.error("MVRV polling error", error=str(e))
                        await asyncio.sleep(60)

        loop.run_until_complete(poll())
        loop.close()

    def get_latest(self) -> Optional[Any]:
        """Retrieves the latest MVRV tick from the Conflation Queue."""
        with self._lock:
            return self.queue[0] if self.queue else None
