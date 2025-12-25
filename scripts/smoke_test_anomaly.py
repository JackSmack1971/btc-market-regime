import numpy as np
from src.intelligence.detector import AnomalyDetector
from src.analyzer import calculate_regime, ScoredMetric
from datetime import datetime

def simulate_anomaly():
    print("### STARTING ANOMALY SMOKE TEST ###")
    
    # 1. Setup normal history
    normal_history = np.random.normal(0, 0.2, (50, 8))
    detector = AnomalyDetector(contamination=0.05)
    detector.fit(normal_history)
    
    # 2. Simulate extreme market event
    # All indicators hit -1.0 (Extreme Bearish Shock)
    extreme_event = np.array([-1.0] * 8)
    
    print(f"Simulating Event: {extreme_event}")
    anomaly_res = detector.detect(extreme_event)
    print(f"Detection Results: {anomaly_res}")
    
    # 3. Verify Integration with calculation
    scored_metrics = [
        ScoredMetric(metric_name=f"m{i}", score=-1.0, raw_value=0.0, confidence="HIGH")
        for i in range(8)
    ]
    
    final_regime = calculate_regime(scored_metrics, anomaly_status=anomaly_res)
    print(f"Final Regime Metadata: {final_regime}")
    
    if final_regime.get('anomaly_alert', {}).get('is_anomaly'):
        print("\n✅ SUCCESS: Anomaly detected and correctly integrated into regime metadata.")
    else:
        print("\n❌ FAILURE: Anomaly was not detected or integrated.")

if __name__ == "__main__":
    simulate_anomaly()
