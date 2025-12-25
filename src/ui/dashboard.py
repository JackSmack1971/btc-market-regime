import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from .charts import plot_regime_history, plot_confluence_heatmap, plot_score_gauge
from ..intelligence.forecaster import RegimeForecaster
from ..backtesting.optimizer import BacktestOptimizer

def render_kpi_section(snapshot: Dict[str, Any]):
    """Renders the top KPI cards and score gauge."""
    label = snapshot['label']
    score = snapshot['score']
    confidence = snapshot['confidence']
    
    label_class = "regime-bull" if label == "BULL" else "regime-bear" if label == "BEAR" else "regime-neutral"
    st.markdown(f"### CURRENT REGIME: <span class='{label_class}'>{label}</span>", unsafe_allow_html=True)
    
    st.metric("Total Score", f"{score:.2f}", help="Aggregated score from -5 to +5.")
    st.metric("Confidence", confidence, help="Reliability of the current signal.")
    
    st.plotly_chart(plot_score_gauge(score), use_container_width=True)

def render_macro_thesis(mtf: Dict[str, Any]):
    """Renders the macro thesis text and confluence heatmap."""
    st.markdown("### MACRO THESIS")
    st.info(mtf['macro_thesis'])
    st.plotly_chart(plot_confluence_heatmap(mtf), use_container_width=True)

def render_component_breakdown(breakdown: List[Dict[str, Any]]):
    """Renders the individual indicator breakdown table."""
    st.markdown("### COMPONENT BREAKDOWN")
    df = pd.DataFrame(breakdown)
    st.dataframe(df[['metric_name', 'score', 'raw_value', 'confidence']], use_container_width=True)

def render_historical_analysis(history: List[Dict[str, Any]], metrics_map: Dict[str, Any]):
    """Renders the historical regime chart with price overlay."""
    btc_prices = pd.DataFrame()
    if 'binance' in metrics_map:
        btc_prices = pd.DataFrame(metrics_map['binance'])
        btc_prices.set_index('timestamp', inplace=True)
    elif 'coingecko' in metrics_map:
        btc_prices = pd.DataFrame(metrics_map['coingecko'])
        btc_prices.set_index('timestamp', inplace=True)

    st.plotly_chart(plot_regime_history(history, btc_prices), use_container_width=True)

def render_forecast_section(history: List[Dict[str, Any]], current_score: float):
    """Renders the experimental forecast engine."""
    if not history:
         st.info("🔮 Forecast engine requires historical data.")
         return

    forecaster = RegimeForecaster(history)
    forecaster.train()
    
    if forecaster.is_trained:
        st.markdown("### 🔮 EXPERIMENTAL FORECAST (Next 12 Hours)")
        forecasts = forecaster.forecast(current_score)
        forecast_df = pd.DataFrame(forecasts)
        st.line_chart(forecast_df.set_index('timestamp'), y='projected_score')
        st.caption("Forecast model: Linear Regression Projection (Experimental)")
    else:
        st.info("🔮 Forecast engine warming up. Accumulating more data...")

def render_optimizer_section(history: List[Dict[str, Any]], metrics_map: Dict[str, Any]):
    """Renders the strategy weight optimizer."""
    with st.expander("🧪 STRATEGY OPTIMIZER (EXPERIMENTAL)"):
        if not history:
            st.info("Optimization requires active session history.")
            return

        st.markdown("Find the optimal mathematical weights for your metrics using Bayesian optimization.")
        if st.button("RUN WEIGHT OPTIMIZATION", use_container_width=True):
            btc_prices = pd.DataFrame() # Reuse logic or pass it down
            if st.button("CONFIRM RUN"): # Nested check or simple run
                 pass
            
            # Simple implementation for now to match app.py
            from ..backtesting.optimizer import BacktestOptimizer
            # Extract price for optimizer
            if 'binance' in metrics_map:
                btc_prices = pd.DataFrame(metrics_map['binance']).set_index('timestamp')
            
            with st.spinner("Optimizing weights via Optuna..."):
                optimizer = BacktestOptimizer(history, btc_prices)
                results = optimizer.run_optimization(n_trials=30)
                if results:
                    st.success(f"Best Correlation: {results['best_value']:.4f}")
                    st.json(results['best_params'])
                    st.info("💡 Update `config/thresholds.yaml` with these values.")

def render_technical_logs(metrics_map: Dict[str, Any], snapshot: Dict[str, Any], mtf: Dict[str, Any]):
    """Renders technical logs and reasoning narrative."""
    with st.expander("🛠️ TECHNICAL LOGS & LOGIC EXPLAINABILITY"):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### RAW DATA STATUS")
            for name, data in metrics_map.items():
                status = "✅ SUCCESS" if data else "❌ FAILED"
                st.write(f"- **{name.upper()}**: {status}")
        
        with col2:
            st.markdown("### REASONING NARRATIVE")
            score = snapshot['score']
            label = snapshot['label']
            
            narrative = f"The Bitcoin market is currently in a **{label}** regime. "
            if score > 3: narrative += "Signals are overwhelmingly bullish."
            elif score > 1: narrative += "Constructive signals dominate."
            elif score > -1: narrative += "Conflicting data points suggest range-bound."
            elif score > -3: narrative += "Defensive signals are emerging."
            else: narrative += "Strong bearish confluence."
            
            st.info(narrative)
            st.code(f"Version: {snapshot['engine_version']} | Score: {score:.2f} | Confluence: {mtf['confluence_score']}%")
