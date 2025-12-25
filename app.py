import streamlit as st
import pandas as pd
from datetime import datetime
from src.fetchers import FetcherFactory
from src.analyzer import RegimeAnalyzer, calculate_regime, analyze_history, analyze_mtf
from src.ui.layout import apply_custom_css, inject_google_fonts
from src.ui.charts import plot_regime_history, plot_confluence_heatmap, plot_score_gauge
from src.utils import logger, health_tracker, alert_manager
from src.intelligence.forecaster import RegimeForecaster
from src.backtesting.optimizer import BacktestOptimizer

# Configuration
SOURCES_PATH = "config/sources.yaml"
THRESHOLDS_PATH = "config/thresholds.yaml"

st.set_page_config(
    page_title="BTC Market Regime Dashboard",
    page_icon="₿",
    layout="wide"
)

# Initialize Engine
@st.cache_resource
def get_analyzer():
    return RegimeAnalyzer(THRESHOLDS_PATH)

def load_sources():
    import yaml
    with open(SOURCES_PATH, 'r') as f:
        return yaml.safe_load(f)['sources']

def play_regime_flip_audio():
    """Injects a subtle audio alert via HTML."""
    # Using a professional notification sound
    sound_url = "https://assets.mixkit.co/active_storage/sfx/2861/2861-preview.mp3"
    st.components.v1.html(
        f"""
        <audio autoplay style="display:none">
            <source src="{sound_url}" type="audio/mpeg">
        </audio>
        """,
        height=0
    )

# UI Entry Point
def main():
    inject_google_fonts()
    apply_custom_css()
    
    st.title("₿ BITCOIN REGIME INTELLIGENCE")
    st.markdown("---")

    sources_config = load_sources()
    analyzer = get_analyzer()

    # Sidebar
    st.sidebar.header("CONTROL CENTER")
    days_hist = st.sidebar.slider("Historical Range (Days)", 7, 60, 30)
    refresh = st.sidebar.button("REFRESH INTELLIGENCE", use_container_width=True)
    
    # API Health HUD
    with st.sidebar.expander("🌐 API OPERATIONAL HEALTH"):
        health_summary = health_tracker.get_latest_status()
        if health_summary:
            for metric, status in health_summary.items():
                icon = "✅" if status['last_success'] else "❌"
                st.markdown(f"{icon} **{metric.upper()}**")
                st.caption(f"Source: {status['last_source']} | Latency: {status['last_latency']:.0f}ms")
        else:
            st.info("No active sessions. Refresh to see API health.")

    # Core Execution
    if refresh or 'metrics_map' not in st.session_state:
        with st.spinner("FETCHING GLOBAL MARKET METRICS..."):
            metrics_map = {}
            scored_snapshot = []
            for name, config in sources_config.items():
                try:
                    fetcher = FetcherFactory.create(name, config)
                    # Fetch enough for MTF/History
                    history_data = fetcher.fetch_history(days_hist)
                    metrics_map[name] = history_data
                    
                    # Latest for snapshot
                    if history_data:
                        scored_snapshot.append(analyzer.score_metric(history_data[-1]))
                except Exception as e:
                    logger.error("UI Fetch failed", metric=name, error=str(e))
            
            st.session_state.metrics_map = metrics_map
            st.session_state.snapshot = calculate_regime(scored_snapshot)
            st.session_state.mtf = analyze_mtf(metrics_map, analyzer)
            st.session_state.history = analyze_history(metrics_map, analyzer)
            
            # 🚨 Regime Flip Detection & Alerts
            if 'previous_regime' in st.session_state:
                prev = st.session_state.previous_regime
                curr = st.session_state.snapshot['label']
                if prev != curr:
                    msg = f"🔔 *BTC REGIME FLIP DETECTED*\n\n"
                    msg += f"**From**: `{prev}`\n"
                    msg += f"**To**: `{curr}`\n\n"
                    msg += f"Score: {st.session_state.snapshot['total_score']:.2f}\n"
                    msg += f"Confidence: {st.session_state.snapshot['confidence']}"
                    alert_manager.send_message(msg)
                    st.toast(f"REGIME FLIP: {prev} -> {curr}", icon="🚨")
                    play_regime_flip_audio()
            
            st.session_state.previous_regime = st.session_state.snapshot['label']

    # PAGE LAYOUT
    col1, col2, col3 = st.columns([1, 1, 1])

    # 1. KPI Cards
    with col1:
        res = st.session_state.snapshot
        label_class = "regime-bull" if res['label'] == "BULL" else "regime-bear" if res['label'] == "BEAR" else "regime-neutral"
        st.markdown(f"### CURRENT REGIME: <span class='{label_class}'>{res['label']}</span>", unsafe_allow_html=True)
        
        # Tooltip explanation for Total Score
        st.metric("Total Score", f"{res['total_score']:.2f}", help="Aggregated score from -5 (Strong Bear) to +5 (Strong Bull). Calculated across all active fetchers.")
        st.metric("Confidence", res['confidence'], help="Weighted average of data source reliability and signal strength.")
        
        # New Score Gauge
        st.plotly_chart(plot_score_gauge(res['total_score']), use_container_width=True)

    # 2. MTF Confluence
    with col2:
        st.markdown("### MACRO THESIS")
        st.info(st.session_state.mtf['macro_thesis'])
        st.plotly_chart(plot_confluence_heatmap(st.session_state.mtf), use_container_width=True)

    # 3. Indicator Breakdown
    with col3:
        st.markdown("### COMPONENT BREAKDOWN")
        breakdown_df = pd.DataFrame(st.session_state.snapshot['breakdown'])
        st.dataframe(breakdown_df[['metric', 'score', 'raw_value', 'confidence']], use_container_width=True)

    st.markdown("---")
    
    # 4. Historical Chart
    # Extract BTC price for overlay if available (e.g. from binance/coingecko fetcher)
    btc_prices = pd.DataFrame()
    if 'binance' in st.session_state.metrics_map:
        btc_prices = pd.DataFrame(st.session_state.metrics_map['binance'])
        btc_prices.set_index('timestamp', inplace=True)
    elif 'coingecko' in st.session_state.metrics_map:
        btc_prices = pd.DataFrame(st.session_state.metrics_map['coingecko'])
        btc_prices.set_index('timestamp', inplace=True)

    st.plotly_chart(plot_regime_history(st.session_state.history, btc_prices), use_container_width=True)

    # 4.1 EXPERIMENTAL FORECAST
    if 'history' in st.session_state and st.session_state.history:
        forecaster = RegimeForecaster(st.session_state.history)
        forecaster.train()
        
        if forecaster.is_trained:
            with st.container():
                st.markdown("### 🔮 EXPERIMENTAL FORECAST (Next 12 Hours)")
                forecasts = forecaster.forecast(st.session_state.snapshot['total_score'])
                forecast_df = pd.DataFrame(forecasts)
                # Simple line chart for forecast
                st.line_chart(forecast_df.set_index('timestamp'), y='projected_score')
                st.caption("Forecast model: Linear Regression Projection (Experimental)")
        else:
            st.info("🔮 Forecast engine warming up. Accumulating more historical points for training...")

    # 4.2 STRATEGY OPTIMIZER
    with st.expander("🧪 STRATEGY OPTIMIZER (EXPERIMENTAL)"):
        if 'history' in st.session_state and st.session_state.history:
            st.markdown("Find the optimal mathematical weights for your metrics using Bayesian optimization.")
            if st.button("RUN WEIGHT OPTIMIZATION", use_container_width=True):
                with st.spinner("Optimizing weights via Optuna..."):
                    optimizer = BacktestOptimizer(st.session_state.history, btc_prices)
                    results = optimizer.run_optimization(n_trials=30)
                    
                    if results:
                        st.success(f"Best Correlation Found: {results['best_value']:.4f}")
                        st.markdown("### SUGGESTED WEIGHTS")
                        st.json(results['best_params'])
                        st.info("💡 Update `config/thresholds.yaml` with these values to improve regime accuracy.")
        else:
            st.info("Optimization requires active session history. Run a refresh first.")

    # 5. Technical Logs & Explainability
    with st.expander("🛠️ TECHNICAL LOGS & LOGIC EXPLAINABILITY"):
        col_logs1, col_logs2 = st.columns([1, 1])
        
        with col_logs1:
            st.markdown("### RAW DATA STATUS")
            for name, data in st.session_state.metrics_map.items():
                status = "✅ SUCCESS" if data else "❌ FAILED"
                st.write(f"- **{name.upper()}**: {status}")
        
        with col_logs2:
            st.markdown("### REASONING NARRATIVE")
            score = res['total_score']
            label = res['label']
            
            narrative = f"The Bitcoin market is currently in a **{label}** regime. "
            if score > 3: narrative += "Signals are overwhelmingly bullish, suggesting high conviction in upward expansion."
            elif score > 1: narrative += "Constructive signals dominate, though some resistance or consolidation is expected."
            elif score > -1: narrative += "Conflicting data points suggest a neutral/range-bound environment."
            elif score > -3: narrative += "Defensive signals are emerging; risk management is prioritized over aggression."
            else: narrative += "Strong bearish confluence indicates broad market weakness and potential further contraction."
            
            st.info(narrative)
            
            st.markdown("### ENGINE METRICS")
            st.code(f"""
Engine Version: {res['engine_version']}
Regime Logic: {res['label']} (Score: {res['total_score']:.2f})
MTF Confluence: {st.session_state.mtf['confluence_score']}%
            """, language="text")

    # Footer
    st.markdown(f"**ENGINE V{st.session_state.snapshot['engine_version']}** | LAST SYNC: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
