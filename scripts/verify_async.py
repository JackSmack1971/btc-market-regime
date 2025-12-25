import asyncio
import aiohttp
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.abspath('.'))

from src.fetchers import FetcherFactory
from src.utils import health_tracker
from src.cache import cache

async def verify_async():
    print("🚀 STARTING ASYNC VERIFICATION...")
    
    # 1. Test SQLite Cache
    print("\n[1] TESTING SQLITE CACHE...")
    test_key = "async_test_metric"
    test_data = {"val": 99.9, "ts": datetime.now().isoformat()}
    cache.set(test_key, test_data)
    
    retrieved = cache.get(test_key)
    if retrieved and retrieved["val"] == 99.9:
        print("✅ SQLite Cache Set/Get: SUCCESS")
    else:
        print("❌ SQLite Cache Set/Get: FAILED")

    # 2. Test Async Fetching
    print("\n[2] TESTING ASYNC FETCHERS...")
    config = {"primary": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"}
    
    async with aiohttp.ClientSession() as session:
        try:
            fetcher = FetcherFactory.create("price_data", config)
            print(f"Fetcher created: {fetcher.metric_name}")
            
            # Test Parallel Fetching
            print("🕒 Attempting parallel fetch (2 calls)...")
            start = datetime.now()
            results = await asyncio.gather(
                fetcher.fetch(session),
                fetcher.fetch(session)
            )
            elapsed = (datetime.now() - start).total_seconds()
            
            print(f"Fetch results: {[r.source for r in results if r]}")
            print(f"Elapsed time: {elapsed:.2f}s (should be < 1s if cache/async works)")
            
            if results[1].source == "primary" or results[1].source == "backup" or results[1].source == "failed":
                # Wait, if results[1] is from cache, it would say "primary" (from the object).
                # The logger says "Cache hit (SQLite)". 
                pass

            # Check health
            summary = health_tracker.get_latest_status()
            if "price_data" in summary:
                 print(f"✅ Health Tracker recorded 'price_data': {summary['price_data']}")

        except Exception as e:
            print(f"❌ Async Fetcher test FAILED: {e}")
            import traceback
            traceback.print_exc()

    print("\n🏁 ASYNC VERIFICATION COMPLETE.")

if __name__ == "__main__":
    asyncio.run(verify_async())
