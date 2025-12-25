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
    """Renders the individual indicator breakdown table with auto-refresh."""
    st.markdown("### COMPONENT BREAKDOWN")
    
    @st.fragment(run_every="0.5s")
    def render_indicators_table():
        """Auto-refreshing HTML table for Top 8 Indicators."""
        if not breakdown:
            st.info("No indicator data available")
            return
        
        # Build HTML table with Finance Green/Bloomberg Red styling
        html = """
        <style>
        .indicators-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            background: rgba(31, 40, 51, 0.4);
            border: 1px solid #45a29e;
            border-radius: 3px;
            overflow: hidden;
            font-feature-settings: "tnum" 1;
        }
        
        .indicators-table thead {
            background: rgba(5, 217, 232, 0.1);
        }
        
        .indicators-table th {
            padding: 12px 16px;
            text-align: left;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 0.75rem;
            color: #05D9E8;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            border-bottom: 2px solid #05D9E8;
        }
        
        .indicators-table tbody tr {
            background: rgba(11, 12, 16, 0.6);
            transition: background 0.15s ease-out;
        }
        
        .indicators-table tbody tr:hover {
            background: rgba(31, 40, 51, 0.7);
        }
        
        .indicators-table td {
            padding: 10px 16px;
            border-bottom: 1px solid rgba(69, 162, 158, 0.2);
        }
        
        /* Label Column: Inter Regular 60% grey */
        .indicator-label {
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.6);
        }
        
        /* Value Columns: JetBrains Mono Bold 100% white */
        .indicator-value {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            font-size: 0.95rem;
            color: rgba(255, 255, 255, 1.0);
            text-align: right;
        }
        
        /* Momentum Signals: Finance Green / Bloomberg Red */
        .momentum-positive {
            color: #4AF6C3;
            text-shadow: 0 0 8px rgba(74, 246, 195, 0.4);
        }
        
        .momentum-negative {
            color: #FF433D;
            text-shadow: 0 0 8px rgba(255, 67, 61, 0.4);
        }
        
        .momentum-neutral {
            color: rgba(255, 255, 255, 0.6);
        }
        
        /* Confidence Badge */
        .confidence-high {
            color: #4AF6C3;
            font-weight: 600;
        }
        
        .confidence-medium {
            color: #FFD60A;
            font-weight: 600;
        }
        
        .confidence-low {
            color: #FF433D;
            font-weight: 600;
        }
        </style>
        
        <table class="indicators-table">
            <thead>
                <tr>
                    <th>INDICATOR</th>
                    <th style="text-align: right;">SCORE</th>
                    <th style="text-align: right;">RAW VALUE</th>
                    <th style="text-align: right;">CONFIDENCE</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for indicator in breakdown[:8]:  # Top 8 indicators
            metric_name = indicator.get('metric_name', 'Unknown')
            score = indicator.get('score', 0.0)
            raw_value = indicator.get('raw_value', 0.0)
            confidence = indicator.get('confidence', 'UNKNOWN')
            
            # Determine momentum class based on score
            if score > 0.5:
                momentum_class = "momentum-positive"
                momentum_symbol = "▲"
            elif score < -0.5:
                momentum_class = "momentum-negative"
                momentum_symbol = "▼"
            else:
                momentum_class = "momentum-neutral"
                momentum_symbol = "●"
            
            # Confidence styling
            if confidence == "HIGH":
                confidence_class = "confidence-high"
            elif confidence == "MEDIUM":
                confidence_class = "confidence-medium"
            else:
                confidence_class = "confidence-low"
            
            # Format raw value
            if isinstance(raw_value, (int, float)):
                if abs(raw_value) >= 1000:
                    raw_value_str = f"{raw_value:,.0f}"
                else:
                    raw_value_str = f"{raw_value:.2f}"
            else:
                raw_value_str = str(raw_value)
            
            html += f"""
                <tr>
                    <td class="indicator-label">{metric_name}</td>
                    <td class="indicator-value {momentum_class}">{momentum_symbol} {score:.2f}</td>
                    <td class="indicator-value">{raw_value_str}</td>
                    <td class="indicator-value {confidence_class}">{confidence}</td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        """
        
        st.html(html)
    
    # Render the auto-refreshing fragment
    render_indicators_table()

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
            st.markdown("### 🧠 INTELLIGENCE BRIEFING")
            reasoning = snapshot.get('reasoning', ["Market logic is currently being calculated..."])
            
            # Display bullet points for each reason
            for item in reasoning:
                st.markdown(f"• {item}")
            
            st.caption(f"Engine Version: {snapshot.get('engine_version', '1.0.0')} | Confluence: {mtf.get('confluence_score', 0)}%")
