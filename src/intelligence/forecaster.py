import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..utils import logger

class RegimeForecaster:
    """Experimental ML Forecaster for predicting future regime scores.
    
    Uses historical score patterns to project the next N hours of market regime.
    """
    
    def __init__(self, history: List[Dict[str, Any]]):
        self.history = history
        self.model = LinearRegression()
        self.is_trained = False
        
    def _prepare_data(self):
        """Converts history list to features and targets."""
        if len(self.history) < 10:
            return None, None
            
        df = pd.DataFrame(self.history)
        # Ensure we use the standardized key 'score'
        # If 'total_score' exists, map it to 'score' for compatibility
        if 'total_score' in df.columns and 'score' not in df.columns:
            df['score'] = df['total_score']
            
        if 'score' not in df.columns:
            return None, None

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Target: score at T+1
        df['target'] = df['score'].shift(-1)
        df = df.dropna()
        
        X = df[['score']].values
        y = df['target'].values
        return X, y

    def train(self):
        """Trains the linear projection model."""
        X, y = self._prepare_data()
        if X is not None and len(X) > 5:
            self.model.fit(X, y)
            self.is_trained = True
            logger.info("Forecaster model trained successfully")
        else:
            logger.warning("Insufficient history for forecaster training")

    def forecast(self, current_score: float, steps: int = 12) -> List[Dict[str, Any]]:
        """Predicts the next N steps of regime scores.
        
        Steps assume hourly increments for the projection.
        """
        if not self.is_trained:
            return []
            
        forecasts = []
        last_score = current_score
        current_time = datetime.now()
        
        for i in range(1, steps + 1):
            next_score = self.model.predict([[last_score]])[0]
            # Add some mean reversion/decay to avoid runaway projections
            next_score = 0.9 * next_score + 0.1 * last_score
            
            projected_time = current_time + timedelta(hours=i)
            forecasts.append({
                "timestamp": projected_time,
                "projected_score": float(next_score),
                "label": "BULL" if next_score > 1 else "BEAR" if next_score < -1 else "NEUTRAL"
            })
            last_score = next_score
            
        return forecasts

    def get_forecast_summary(self) -> str:
        """Returns a human-readable forecast summary."""
        if not self.is_trained:
            return "Insufficient data for forecasting."
        
        return "Model trained on history. Projections active."
