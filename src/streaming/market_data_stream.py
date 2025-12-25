"""
MarketDataStream: Producer-Consumer pattern for high-frequency market data ingestion.

Architecture:
- Producer: Background thread running uvloop event loop
- Consumer: Streamlit main thread reading from deque
- Buffer: collections.deque(maxlen=1) for latest data only
"""

import asyncio
import threading
from collections import deque
from typing import Dict, Any, Optional
import time

try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False

import aiohttp
from src.fetchers import FetcherFactory
from src.utils import logger


class MarketDataStream:
    """
    Producer-Consumer pattern for high-frequency market data ingestion.
    
    Usage:
        stream = MarketDataStream(sources_config, days_hist=30)
        stream.start()
        
        # Later, in Streamlit main thread:
        latest_data = stream.get_latest()
        
        # Cleanup:
        stream.stop()
    """
    
    def __init__(self, sources_config: Dict, days_hist: int = 30, refresh_interval: int = 60):
        """
        Initialize the market data stream.
        
        Args:
            sources_config: Dictionary of data source configurations
            days_hist: Number of days of historical data to fetch
            refresh_interval: Seconds between data refreshes (default: 60)
        """
        self.sources_config = sources_config
        self.days_hist = days_hist
        self.refresh_interval = refresh_interval
        
        # Thread-safe deque (maxlen=1 keeps only latest data)
        self.data_buffer = deque(maxlen=1)
        
        # Control flags
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Performance tracking
        self._fetch_count = 0
        self._error_count = 0
        
        logger.info("MarketDataStream initialized", 
                   sources=len(sources_config), 
                   days_hist=days_hist,
                   refresh_interval=refresh_interval,
                   uvloop_available=UVLOOP_AVAILABLE)
    
    def start(self):
        """Start the background producer thread."""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run_producer, daemon=True, name="MarketDataProducer")
            self._thread.start()
            logger.info("MarketDataStream started", thread_id=self._thread.ident)
    
    def stop(self):
        """Stop the background producer thread."""
        if self._running:
            self._running = False
            if self._loop and self._loop.is_running():
                self._loop.call_soon_threadsafe(self._loop.stop)
            logger.info("MarketDataStream stopped", 
                       fetch_count=self._fetch_count, 
                       error_count=self._error_count)
    
    def _run_producer(self):
        """Producer: Runs in background thread with uvloop (if available)."""
        # Install uvloop as the event loop for better performance
        if UVLOOP_AVAILABLE:
            uvloop.install()
            logger.info("uvloop installed for high-performance async")
        
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        try:
            self._loop.run_until_complete(self._fetch_loop())
        except Exception as e:
            logger.error("Producer thread crashed", error=str(e))
        finally:
            self._loop.close()
            logger.info("Producer event loop closed")
    
    async def _fetch_loop(self):
        """Continuous async fetch loop."""
        async with aiohttp.ClientSession() as session:
            while self._running:
                fetch_start = time.time()
                
                try:
                    # Fetch all metrics concurrently
                    tasks = []
                    for name, config in self.sources_config.items():
                        fetcher = FetcherFactory.create(name, config)
                        tasks.append(fetcher.fetch_history(session, self.days_hist))
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Map results to metric names
                    metrics_map = {}
                    names = list(self.sources_config.keys())
                    for i, result in enumerate(results):
                        name = names[i]
                        if isinstance(result, Exception):
                            logger.error("Stream fetch failed", metric=name, error=str(result))
                            metrics_map[name] = []
                            self._error_count += 1
                        else:
                            metrics_map[name] = result
                    
                    # Push to buffer (thread-safe)
                    fetch_duration = time.time() - fetch_start
                    self.data_buffer.append({
                        'metrics_map': metrics_map,
                        'timestamp': time.time(),
                        'fetch_duration': fetch_duration
                    })
                    
                    self._fetch_count += 1
                    logger.info("Data stream updated", 
                               fetch_duration=f"{fetch_duration:.2f}s",
                               metrics_count=len(metrics_map),
                               fetch_count=self._fetch_count)
                    
                    # Wait for next refresh interval
                    await asyncio.sleep(self.refresh_interval)
                    
                except Exception as e:
                    logger.error("Fetch loop error", error=str(e))
                    self._error_count += 1
                    await asyncio.sleep(5)  # Backoff on error
    
    def get_latest(self) -> Optional[Dict[str, Any]]:
        """
        Consumer: Get latest data from buffer.
        
        Returns:
            Dictionary with 'metrics_map', 'timestamp', and 'fetch_duration'
            or None if no data available yet.
        """
        try:
            return self.data_buffer[-1] if self.data_buffer else None
        except IndexError:
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get stream performance statistics."""
        return {
            'running': self._running,
            'fetch_count': self._fetch_count,
            'error_count': self._error_count,
            'buffer_size': len(self.data_buffer),
            'uvloop_enabled': UVLOOP_AVAILABLE,
            'thread_alive': self._thread.is_alive() if self._thread else False
        }
    
    def __del__(self):
        """Cleanup on garbage collection."""
        self.stop()
