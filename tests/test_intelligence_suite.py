import unittest
import numpy as np
from datetime import datetime, timedelta
from src.intelligence.detector import AnomalyDetector
from src.intelligence.forecaster import RegimeForecaster

class TestIntelligenceSuite(unittest.TestCase):
    # ========== ANOMALY DETECTOR TESTS ==========
    def test_detector_not_fitted(self):
        detector = AnomalyDetector()
        with self.assertRaises(RuntimeError):
            detector.detect(np.array([1, 2, 3]))

    def test_detector_fit_insufficient_data(self):
        detector = AnomalyDetector()
        data = np.random.rand(5, 8)
        detector.fit(data)
        self.assertFalse(detector.is_fitted)

    def test_detector_happy_path(self):
        detector = AnomalyDetector(contamination=0.1)
        # 20 samples of 8 features
        history = np.random.normal(0, 1, (20, 8))
        detector.fit(history)
        self.assertTrue(detector.is_fitted)
        
        # Detect normal
        res = detector.detect(np.zeros(8))
        self.assertIn("is_anomaly", res)
        self.assertFalse(res["is_anomaly"])
        self.assertEqual(res["severity"], "LOW")

    def test_detector_anomaly_severity(self):
        detector = AnomalyDetector(contamination=0.1)
        # Cluster of data
        history = np.random.normal(0, 0.1, (50, 8))
        detector.fit(history)
        
        # Extreme outlier
        outlier = np.array([10.0] * 8)
        res = detector.detect(outlier)
        self.assertTrue(res["is_anomaly"])
        # High decision scores (negative) mean high severity
        self.assertIn(res["severity"], ["MEDIUM", "HIGH"])

    # ========== FORECASTER TESTS ==========
    def test_forecaster_insufficient_data(self):
        forecaster = RegimeForecaster([])
        forecaster.train()
        self.assertFalse(forecaster.is_trained)
        self.assertEqual(len(forecaster.forecast(0.0)), 0)

    def test_forecaster_happy_path(self):
        history = [
            {"score": float(i), "timestamp": (datetime.now() - timedelta(hours=i)).isoformat()}
            for i in range(15)
        ]
        forecaster = RegimeForecaster(history)
        forecaster.train()
        self.assertTrue(forecaster.is_trained)
        
        forecasts = forecaster.forecast(current_score=14.0, steps=6)
        self.assertEqual(len(forecasts), 6)
        # Check structure
        self.assertIn("projected_score", forecasts[0])
        self.assertIn("label", forecasts[0])
        # Prediction should trend upwards given the history (0 to 14)
        self.assertGreater(forecasts[0]["projected_score"], 10.0)

    def test_forecaster_legacy_key_support(self):
        history = [
            {"total_score": float(i), "timestamp": (datetime.now() - timedelta(hours=i)).isoformat()}
            for i in range(15)
        ]
        forecaster = RegimeForecaster(history)
        forecaster.train()
        self.assertTrue(forecaster.is_trained)
        
        forecasts = forecaster.forecast(current_score=14.0, steps=1)
        self.assertEqual(len(forecasts), 1)

if __name__ == "__main__":
    unittest.main()
