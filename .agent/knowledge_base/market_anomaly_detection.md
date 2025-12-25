# MARKET ANOMALY DETECTION (Pattern #10)

## Context
Market regimes can shift abruptly due to black swan events, flash crashes, or extreme narrative shifts. Standard threshold scoring may lag or fail to capture the multi-dimensional nature of these shocks.

## Implementation Pattern (Isolation Forest)
- **Model Choice**: `sklearn.ensemble.IsolationForest`.
- **Reasoning**: Isolation Forest is an unsupervised algorithm that is highly effective at detecting outliers in high-dimensional datasets without requiring labeled training data.
- **Workflow**:
    1. **Vectorization**: Transform the `breakdown` of indicators into a fixed-length vector (e.g., 8 scores).
    2. **History-Aware**: Fit the model on the latest N days of historical regime data during each dashboard refresh.
    3. **Thresholding**: Use the `decision_function` to derive an anomaly score.
    4. **Severity Mapping**:
        - `is_anomaly=True` AND `decision_score > -0.2`: MEDIUM Severity.
        - `is_anomaly=True` AND `decision_score <= -0.2`: HIGH Severity.

## Best Practices
- **Minimum Data**: Require at least 10 samples before fitting to prevent noise from being classified as an anomaly.
- **Contamination**: Set a conservative `contamination` parameter (e.g., 0.05) to avoid over-alerting on normal volatility.
- **Feature Consistency**: Ensure metrics are sorted by name before vectorization to maintain feature alignment.
