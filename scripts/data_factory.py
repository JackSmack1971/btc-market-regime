import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add src to path
sys.path.append(os.path.abspath('.'))

from src.models import MetricData

def generate_mock_history(days=30):
    print(f"🏭 DATA FACTORY: Generating {days} days of high-fidelity market data...")
    
    cache_dir = Path(".cache")
    cache_dir.mkdir(exist_ok=True)
    
    # 1. Base Price (Geometric Brownian Motion)
    mu = 0.0001  # Slight upward drift
    sigma = 0.03  # Volatility
    s0 = 98000    # Start price
    dt = 1
    
    prices = [s0]
    for _ in range(days * 24 - 1): # Hourly stats
        prices.append(prices[-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.normal()))
    
    # Decimate to daily for the 30-day view
    daily_prices = [prices[i] for i in range(0, len(prices), 24)]
    
    metrics = {
        "price_data": daily_prices,
        "fear_greed_index": [50 + (p - s0)/1000 + np.random.normal(0, 5) for p in daily_prices],
        "mvrv_ratio": [1.5 + (p - s0)/20000 + np.random.normal(0, 0.1) for p in daily_prices],
        "perpetual_funding_rates": [0.01 + (p - daily_prices[i-1 if i > 0 else 0])/10000 for i, p in enumerate(daily_prices)],
        "hash_rate": [700 + i*2 + np.random.normal(0, 10) for i in range(days)],
        "exchange_net_flows": [np.random.normal(-500, 200) for _ in range(days)],
        "active_addresses": [900000 + (p - s0)/10 + np.random.normal(0, 50000) for p in daily_prices],
        "open_interest": [15e9 + (p - s0)*1e5 + np.random.normal(0, 1e8) for p in daily_prices]
    }
    
    # Constrain values
    metrics["fear_greed_index"] = [max(0, min(100, v)) for v in metrics["fear_greed_index"]]
    
    start_time = datetime.now() - timedelta(days=days)
    
    for name, values in metrics.items():
        history = []
        for i, val in enumerate(values):
            ts = start_time + timedelta(days=i)
            history.append(MetricData(
                metric_name=name,
                value=float(val),
                timestamp=ts,
                source="factory"
            ))
        
        # Save History
        history_key = f"{name}_history_{days}"
        with open(cache_dir / f"{history_key}.pkl", 'wb') as f:
            pickle.dump(history, f)
            
        # Save Latest
        latest_key = f"{name}_latest"
        with open(cache_dir / f"{latest_key}.pkl", 'wb') as f:
            pickle.dump(history[-1], f)
            
        print(f"✅ Generated {name}: {len(history)} entries cached.")

    print("\n🏁 DATA FACTORY COMPLETED. Dashboard is now primed.")

if __name__ == "__main__":
    generate_mock_history(30)
