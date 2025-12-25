import pytest
import pandas as pd
from src.backtesting.optimizer import BacktestOptimizer

def test_optimizer_insufficient_data():
    optimizer = BacktestOptimizer([], pd.DataFrame())
    results = optimizer.run_optimization(n_trials=5)
    assert results == {}

def test_optimizer_basic_optimization():
    # Mock history and price data
    history = [
        {"score": float(i % 5 - 2), "timestamp": "2023-01-01"} 
        for i in range(10)
    ]
    price_df = pd.DataFrame({
        "price": [100 + i for i in range(10)]
    })
    
    optimizer = BacktestOptimizer(history, price_df)
    results = optimizer.run_optimization(n_trials=5)
    
    assert "best_params" in results
    assert "best_value" in results
    assert isinstance(results["best_value"], float)
    # Check if we got weights back
    assert "fear_greed_weight" in results["best_params"]
