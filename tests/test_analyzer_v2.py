import unittest
from datetime import datetime, timedelta
from src.analyzer import (
    RegimeAnalyzer, ThresholdScorer, InverseThresholdScorer, 
    MultiplierScorer, MomentumScorer, analyze_history, 
    analyze_mtf, get_metric_narrative, calculate_regime
)
from src.models import MetricData, ScoredMetric

class TestAnalyzerV2(unittest.TestCase):
    def setUp(self):
        # Create a temp thresholds file for RegimeAnalyzer
        self.thresholds_content = """
metrics:
  fear_greed_index: {bull: 75, bear: 25, weight: 1.5}
  mvrv_ratio: {bull: 1.2, bear: 3.5, weight: 2.0}
  rsi: {bull: 30, bear: 70, weight: 1.0}
  hash_rate: {bull_multiplier: 1.05, bear_multiplier: 0.95, weight: 1.2}
  active_addresses: {bull_mom: 0.05, bear_mom: -0.05, weight: 1.0}
        """
        self.thresholds_path = "tests/temp_thresholds.yaml"
        with open(self.thresholds_path, "w") as f:
            f.write(self.thresholds_content)
        self.analyzer = RegimeAnalyzer(self.thresholds_path)

    # ========== SCORER STRATEGY TESTS ==========
    def test_threshold_scorer(self):
        scorer = ThresholdScorer()
        t = {"bull": 75, "bear": 25}
        self.assertEqual(scorer.score(80, t), 1.0)
        self.assertEqual(scorer.score(20, t), -1.0)
        self.assertEqual(scorer.score(50, t), 0.0)

    def test_inverse_threshold_scorer(self):
        scorer = InverseThresholdScorer()
        t = {"bull": 1.2, "bear": 3.5}
        self.assertEqual(scorer.score(1.0, t), 1.0)
        self.assertEqual(scorer.score(4.0, t), -1.0)
        self.assertEqual(scorer.score(2.0, t), 0.0)

    def test_multiplier_scorer(self):
        scorer = MultiplierScorer()
        t = {"bull_multiplier": 1.1, "bear_multiplier": 0.9}
        self.assertEqual(scorer.score(1.2, t), 1.0)
        self.assertEqual(scorer.score(0.8, t), -1.0)
        self.assertEqual(scorer.score(1.0, t), 0.0)

    def test_momentum_scorer(self):
        scorer = MomentumScorer()
        t = {"bull_mom": 0.1, "bear_mom": -0.1}
        self.assertEqual(scorer.score(0.2, t), 1.0)
        self.assertEqual(scorer.score(-0.2, t), -1.0)
        self.assertEqual(scorer.score(0.0, t), 0.0)

    # ========== REGIME ANALYZER TESTS ==========
    def test_score_metric_happy_path(self):
        data = MetricData(metric_name="fear_greed_index", value=80, timestamp=datetime.now(), source="primary")
        scored = self.analyzer.score_metric(data)
        self.assertEqual(scored.score, 1.5) # 1.0 * 1.5 weight
        self.assertEqual(scored.confidence, "HIGH")

    def test_score_metric_fallback(self):
        data = MetricData(metric_name="mvrv_ratio", value=1.0, timestamp=datetime.now(), source="backup")
        scored = self.analyzer.score_metric(data)
        self.assertEqual(scored.score, 2.0) # 1.0 * 2.0 weight
        self.assertEqual(scored.confidence, "MEDIUM")
        self.assertTrue(scored.is_fallback)

    def test_score_metric_failed_source(self):
        data = MetricData(metric_name="rsi", value=20, timestamp=datetime.now(), source="failed")
        scored = self.analyzer.score_metric(data)
        self.assertEqual(scored.score, 0.0)
        self.assertEqual(scored.confidence, "LOW")

    # ========== HISTORY & MTF TESTS ==========
    def test_analyze_history(self):
        now = datetime.now()
        metrics_map = {
            "fear_greed_index": [
                MetricData(metric_name="fear_greed_index", value=80, timestamp=now - timedelta(days=1), source="primary"),
                MetricData(metric_name="fear_greed_index", value=20, timestamp=now, source="primary")
            ]
        }
        results = analyze_history(metrics_map, self.analyzer)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["label"], "SIDEWAYS/TRANSITIONAL") # Score 1.5 (threshold 3)
        self.assertEqual(results[1]["label"], "SIDEWAYS/TRANSITIONAL") # Score -1.5

    def test_analyze_mtf_confluence(self):
        now = datetime.now()
        # Create 30 days of bullish data
        metrics_map = {
            "fear_greed_index": [
                MetricData(metric_name="fear_greed_index", value=90, timestamp=now - timedelta(days=i), source="primary")
                for i in range(31)
            ]
        }
        # In this config, FG 90 = score 1.0 * 1.5 = 1.5. 
        # But for BULL we need score > 3. Let's add more metrics.
        metrics_map["mvrv_ratio"] = [
            MetricData(metric_name="mvrv_ratio", value=1.0, timestamp=now - timedelta(days=i), source="primary")
            for i in range(31)
        ] # Score 1.0 * 2.0 = 2.0. Total = 3.5 (> 3)
        
        results = analyze_mtf(metrics_map, self.analyzer)
        self.assertEqual(results["daily"]["label"], "BULL")
        self.assertEqual(results["weekly"]["label"], "BULL")
        self.assertEqual(results["monthly"]["label"], "BULL")
        self.assertIn("FULL BULLISH CONFLUENCE", results["macro_thesis"])
        self.assertEqual(results["confluence_score"], 100)

    # ========== NARRATIVE & AGGREGATION TESTS ==========
    def test_get_metric_narrative(self):
        s = get_metric_narrative("fear_greed_index", 1.5, 80)
        self.assertIn("Fear & Greed Index", s)
        self.assertIn("Extreme Greed", s)
        self.assertIn("Bullish", s)

    def test_calculate_regime_empty(self):
        res = calculate_regime([])
        self.assertEqual(res["label"], "DATA UNAVAILABLE")
        self.assertEqual(res["score"], 0.0)

    def test_calculate_regime_mixed_confidence(self):
        metrics = [
            ScoredMetric(metric_name="m1", score=2.0, raw_value=1.0, confidence="LOW"),
            ScoredMetric(metric_name="m2", score=2.0, raw_value=1.0, confidence="LOW"),
            ScoredMetric(metric_name="m3", score=2.0, raw_value=1.0, confidence="HIGH"),
        ]
        # low_confidence_pct = 2/3 = 0.66 > 0.6 -> LOW confidence
        res = calculate_regime(metrics)
        self.assertEqual(res["confidence"], "LOW")
        self.assertEqual(res["label"], "BULL") # total score 6.0 > 3

if __name__ == "__main__":
    unittest.main()
