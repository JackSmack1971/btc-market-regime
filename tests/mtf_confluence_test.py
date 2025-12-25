import unittest
from datetime import datetime, timedelta
from src.models import MetricData, ScoredMetric
from src.analyzer import RegimeAnalyzer, calculate_regime, analyze_history

class TestMTFConfluence(unittest.TestCase):
    def setUp(self):
        self.analyzer = RegimeAnalyzer("config/thresholds.yaml")

    def test_temporal_aggregation_logic(self):
        """Verify that multiple days of data can be collapsed into a single timeframe score."""
        # Create 30 days of bullish data
        start_date = datetime.now() - timedelta(days=30)
        daily_data = [
            MetricData(metric_name="fear_greed_index", value=80.0, timestamp=start_date + timedelta(days=i), source="primary")
            for i in range(30)
        ]
        
        # Simple average-based aggregation logic test (to be implemented in analyzer.py)
        avg_value = sum(d.value for d in daily_data) / len(daily_data)
        self.assertEqual(avg_value, 80.0)
        
        scored = self.analyzer.score_metric(MetricData(
            metric_name="fear_greed_index", 
            value=avg_value, 
            timestamp=datetime.now(), 
            source="primary"
        ))
        self.assertEqual(scored.score, 1.0) # Weighted score based on thresholds

    def test_macro_thesis_generation(self):
        """Verify the 'Macro Advisor' logic for trend alignment."""
        # Mock regimes
        daily = {"label": "BULL", "total_score": 4.5}
        weekly = {"label": "BULL", "total_score": 3.8}
        monthly = {"label": "BULL", "total_score": 5.2}
        
        # Confluence check (to be implemented)
        def get_thesis(d, w, m):
            labels = [d['label'], w['label'], m['label']]
            if all(l == "BULL" for l in labels):
                return "FULL BULLISH ALIGNMENT"
            return "MIXED"
            
        self.assertEqual(get_thesis(daily, weekly, monthly), "FULL BULLISH ALIGNMENT")

if __name__ == '__main__':
    unittest.main()
