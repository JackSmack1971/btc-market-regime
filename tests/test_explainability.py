import unittest
from datetime import datetime
from src.analyzer import RegimeAnalyzer, calculate_regime
from src.models import ScoredMetric

class TestExplainability(unittest.TestCase):
    """Tests for the Market Logic Explainability engine."""

    def test_reasoning_generation_bullish(self):
        """Verify that high positive scores generate bullish reasoning."""
        metrics = [
            ScoredMetric(metric_name="fear_greed_index", score=1.5, raw_value=75.0, confidence="HIGH"),
            ScoredMetric(metric_name="perpetual_funding_rates", score=1.0, raw_value=0.015, confidence="HIGH"),
            ScoredMetric(metric_name="rsi", score=0.5, raw_value=65.0, confidence="HIGH")
        ]
        
        analysis = calculate_regime(metrics)
        
        self.assertIn('reasoning', analysis)
        reasoning = analysis['reasoning']
        self.assertIsInstance(reasoning, list)
        self.assertTrue(len(reasoning) > 0)
        
        # Check for specific keywords based on top drivers
        bullish_keywords = ["Greed", "Bullish", "High", "Positive"]
        found = any(keyword.lower() in str(reasoning).lower() for keyword in bullish_keywords)
        self.assertTrue(found, f"Reasoning does not contain bullish keywords: {reasoning}")

    def test_reasoning_generation_bearish(self):
        """Verify that high negative scores generate bearish reasoning."""
        metrics = [
            ScoredMetric(metric_name="fear_greed_index", score=-1.5, raw_value=25.0, confidence="HIGH"),
            ScoredMetric(metric_name="perpetual_funding_rates", score=-1.0, raw_value=-0.01, confidence="HIGH"),
            ScoredMetric(metric_name="rsi", score=-0.8, raw_value=35.0, confidence="HIGH")
        ]
        
        analysis = calculate_regime(metrics)
        
        reasoning = analysis['reasoning']
        bearish_keywords = ["Fear", "Bearish", "Low", "Negative", "Oversold"]
        found = any(keyword.lower() in str(reasoning).lower() for keyword in bearish_keywords)
        self.assertTrue(found, f"Reasoning does not contain bearish keywords: {reasoning}")

    def test_top_driver_priority(self):
        """Verify that the reasoning engine prioritizes the highest magnitude scores."""
        metrics = [
            ScoredMetric(metric_name="fear_greed_index", score=0.1, raw_value=51.0, confidence="HIGH"),
            ScoredMetric(metric_name="hash_rate", score=-2.0, raw_value=450.0, confidence="HIGH"), # Highest magnitude
            ScoredMetric(metric_name="rsi", score=0.2, raw_value=55.0, confidence="HIGH")
        ]
        
        analysis = calculate_regime(metrics)
        reasoning = str(analysis['reasoning'])
        
        # Hash rate should be the primary focus of the reasoning
        self.assertIn("Hash Rate", reasoning)
        self.assertIn("Bearish", reasoning)

    def test_empty_metrics_graceful_reasoning(self):
        """Verify that empty metrics return a neutral fallback reasoning."""
        analysis = calculate_regime([])
        self.assertIn('reasoning', analysis)
        self.assertIn("No data", str(analysis['reasoning']))

if __name__ == '__main__':
    unittest.main()
