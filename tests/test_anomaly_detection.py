import unittest
import numpy as np
from src.intelligence.detector import AnomalyDetector

class TestAnomalyDetection(unittest.TestCase):
    """Tests for the Anomaly Detection ML system."""

    def setUp(self):
        # Initialize with low contamination for testing sensitivity
        self.detector = AnomalyDetector(contamination=0.1)
        
        # Generate synthetic normal data (8 indicators)
        # Random noise around 0.0 (sideways/transitional)
        self.normal_data = np.random.normal(0, 0.5, (100, 8))
        self.normal_data = np.clip(self.normal_data, -1.0, 1.0)

    def test_training_and_detection_normal(self):
        """Verify that normal data points are classified as non-anomalous."""
        self.detector.fit(self.normal_data)
        
        # Test a standard "normal" point
        current_scores = np.array([0.1, -0.1, 0.2, 0.0, -0.2, 0.1, 0.0, -0.1])
        result = self.detector.detect(current_scores)
        
        self.assertIn('is_anomaly', result)
        self.assertFalse(result['is_anomaly'])
        self.assertEqual(result['severity'], "LOW")

    def test_outlier_detection_extreme_spike(self):
        """Verify that extreme metric spikes trigger an anomaly alert."""
        self.detector.fit(self.normal_data)
        
        # Injection: An extreme outlier (e.g., all indicators hitting max)
        extreme_scores = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
        result = self.detector.detect(extreme_scores)
        
        self.assertTrue(result['is_anomaly'])
        self.assertIn(result['severity'], ["MEDIUM", "HIGH"])

    def test_severity_levels(self):
        """Verify that severity maps correctly to anomaly scores."""
        self.detector.fit(self.normal_data)
        
        # We need to access internal score to verify mapping logic
        # High severity check (force a very odd point)
        extreme_point = np.array([-5.0] * 8) 
        result = self.detector.detect(extreme_point)
        
        self.assertTrue(result['is_anomaly'])
        self.assertEqual(result['severity'], "HIGH")

    def test_unfitted_model_error(self):
        """Verify that detect() fails gracefully if model isn't fitted."""
        new_detector = AnomalyDetector()
        with self.assertRaises(RuntimeError):
            new_detector.detect(np.zeros(8))

if __name__ == '__main__':
    unittest.main()
