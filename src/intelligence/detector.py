import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, Optional
from ..utils import logger

class AnomalyDetector:
    """Unsupervised anomaly detection using Isolation Forest."""

    def __init__(self, contamination: float = 0.05):
        """
        Args:
            contamination: The proportion of outliers in the data set. 
                          Used to define the threshold on the decision function.
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.is_fitted = False

    def fit(self, historical_data: np.ndarray):
        """
        Fits the Isolation Forest model on historical regime scores.
        
        Args:
            historical_data: Array of shape (n_samples, n_features) 
                            containing historical metric scores.
        """
        if len(historical_data) < 10:
            logger.warning("Anomaly detector requires at least 10 samples to fit properly.")
            return

        try:
            self.model.fit(historical_data)
            self.is_fitted = True
            logger.info("Anomaly detector successfully fitted", samples=len(historical_data))
        except Exception as e:
            logger.error("Failed to fit anomaly detector", error=str(e))

    def detect(self, current_scores: np.ndarray) -> Dict[str, Any]:
        """
        Detects if current market scores constitute an anomaly.
        
        Args:
            current_scores: Array of current indicator scores.
            
        Returns:
            Dict containing 'is_anomaly', 'anomaly_score', and 'severity'.
        """
        if not self.is_fitted:
            raise RuntimeError("AnomalyDetector must be fitted before calling detect().")

        # Reshape to (1, n_features) for scikit-learn
        X = current_scores.reshape(1, -1)
        
        # decision_function returns the anomaly score (lower is more anomalous)
        # IsolationForest returns -1 for anomalies, 1 for normal
        decision_score = self.model.decision_function(X)[0]
        prediction = self.model.predict(X)[0]
        
        is_anomaly = (prediction == -1)
        
        # Severity mapping
        if not is_anomaly:
            severity = "LOW"
        else:
            if decision_score < -0.2:
                severity = "HIGH"
            else:
                severity = "MEDIUM"

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": float(decision_score),
            "severity": severity
        }
