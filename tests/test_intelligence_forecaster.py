import pytest
from datetime import datetime, timedelta
from src.intelligence.forecaster import RegimeForecaster

def test_forecaster_insufficient_data():
    # Only 5 points, needs 10
    history = [{"total_score": 1.0, "timestamp": datetime.now() - timedelta(hours=i)} for i in range(5)]
    forecaster = RegimeForecaster(history)
    forecaster.train()
    assert not forecaster.is_trained
    assert forecaster.forecast(1.0) == []

def test_forecaster_training_and_projection():
    # 20 points, enough for training
    history = [
        {"total_score": float(i % 5), "timestamp": datetime.now() - timedelta(hours=i)} 
        for i in range(20)
    ]
    forecaster = RegimeForecaster(history)
    forecaster.train()
    assert forecaster.is_trained
    
    projection = forecaster.forecast(2.0, steps=6)
    assert len(projection) == 6
    assert "projected_score" in projection[0]
    assert isinstance(projection[0]["projected_score"], float)

def test_forecaster_empty_history():
    forecaster = RegimeForecaster([])
    forecaster.train()
    assert not forecaster.is_trained
    assert forecaster.forecast(1.0) == []
