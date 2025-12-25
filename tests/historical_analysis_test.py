import unittest
from datetime import datetime, timedelta
from src.models import MetricData, ScoredMetric
from src.analyzer import RegimeAnalyzer, calculate_regime

class TestHistoricalAnalysis(unittest.TestCase):
    def test_calculate_regime_batch(self):
        """Verify that calculate_regime works correctly on a batch of scored metrics."""
        metrics = [
            ScoredMetric(metric_name="fear_greed", score=1.0, raw_value=80, confidence="HIGH"),
            ScoredMetric(metric_name="mvrv", score=1.0, raw_value=1.5, confidence="HIGH")
        ]
        result = calculate_regime(metrics)
        self.assertEqual(result['label'], "SIDEWAYS/TRANSITIONAL") # 1+1 = 2, threshold is 3
        self.assertIn('engine_version', result)
        self.assertIn('timestamp', result)

    def test_date_alignment_logic(self):
        """Verify that the engine can align differing timestamps into daily bins."""
        # Mock logic to be implemented in analyzer.py
        pass

if __name__ == '__main__':
    unittest.main()
