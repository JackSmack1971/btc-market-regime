import asyncio
import aiohttp
import streamlit as st
import pandas as pd
from datetime import datetime
from src.fetchers import FetcherFactory
from src.analyzer import RegimeAnalyzer, calculate_regime, analyze_history, analyze_mtf
from src.ui.layout import apply_custom_css, inject_google_fonts
from src.ui.charts import plot_regime_history, plot_confluence_heatmap, plot_score_gauge
from src.utils import logger, health_tracker, alert_manager
from src.intelligence.forecaster import RegimeForecaster
from src.intelligence.detector import AnomalyDetector
from src.backtesting.optimizer import BacktestOptimizer
import numpy as np

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
    
    # Live Connection Beacon + Title
    st.markdown('<span class="live-beacon"></span>', unsafe_allow_html=True)
    st.title("₿ BITCOIN REGIME INTELLIGENCE")
    st.markdown("---")

    sources_config = load_sources()
    analyzer = get_analyzer()

    # Sidebar: COMMAND LINK
    st.sidebar.header("⚡ COMMAND LINK")
    days_hist = st.sidebar.slider("Historical Range (Days)", 7, 60, 30)
    refresh = st.sidebar.button("⟁ REFRESH INTELLIGENCE", use_container_width=True)
    
    # API Health HUD (System Health Matrix)
    with st.sidebar.expander("🌐 SYSTEM HEALTH", expanded=False):
        health_summary = health_tracker.get_latest_status()
        if health_summary:
            # Horizontal chip layout
            chips_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px;">'
            for metric, status in health_summary.items():
                dot_class = "health-dot-success" if status['last_success'] else "health-dot-failure"
                metric_abbr = metric[:3].upper()
                chips_html += f'''
                    <div class="health-chip">
                        <div class="{dot_class}"></div>
                        <span>{metric_abbr}</span>
                    </div>
                '''
            chips_html += '</div>'
            st.markdown(chips_html, unsafe_allow_html=True)
        else:
            st.info("No active sessions. Refresh to see system health.")

    # Core Execution (Async Orchestration)
    async def fetch_all_metrics():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for name, config in sources_config.items():
                fetcher = FetcherFactory.create(name, config)
                tasks.append(fetcher.fetch_history(session, days_hist))
            
            return await asyncio.gather(*tasks, return_exceptions=True)

    if refresh or 'metrics_map' not in st.session_state:
        with st.spinner("FETCHING GLOBAL MARKET METRICS (ASYNC)..."):
            results = asyncio.run(fetch_all_metrics())
            
            metrics_map = {}
            scored_snapshot = []
            
            # Map results back to metric names
            names = list(sources_config.keys())
            for i, result in enumerate(results):
                name = names[i]
                if isinstance(result, Exception):
                    logger.error("UI Fetch failed", metric=name, error=str(result))
                    metrics_map[name] = []
                else:
                    metrics_map[name] = result
                    if result:
                        scored_snapshot.append(analyzer.score_metric(result[-1]))
            
            st.session_state.metrics_map = metrics_map
            st.session_state.snapshot = calculate_regime(scored_snapshot)
            st.session_state.mtf = analyze_mtf(metrics_map, analyzer)
            st.session_state.history = analyze_history(metrics_map, analyzer)
            
            # Anomaly Detection Training & Execution
            if st.session_state.history:
                # Prepare historical data for detector (N days x 8 features)
                # We need to reconstruct the feature matrix from metrics_map
                hist_matrix = []
                # Ensure we only use dates where we have a full set of metrics
                # For simplicity in this iteration, we'll use the breakdown from analyze_history
                for entry in st.session_state.history:
                    # Sort breakdown by metric name for consistent vectorization
                    sorted_b = sorted(entry['breakdown'], key=lambda x: x['metric_name'])
                    vector = [m['score'] for m in sorted_b]
                    # Only add if we have the full set of 8 indicators
                    if len(vector) == 8:
                        hist_matrix.append(vector)
                
                if len(hist_matrix) >= 10:
                    detector = AnomalyDetector(contamination=0.05)
                    detector.fit(np.array(hist_matrix))
                    
                    # Detect in current snapshot
                    current_vector = np.array([m.score for m in sorted(scored_snapshot, key=lambda x: x.metric_name)])
                    anomaly_res = detector.detect(current_vector)
                    
                    # Update snapshot with anomaly data
                    st.session_state.snapshot = calculate_regime(scored_snapshot, anomaly_status=anomaly_res)
            
            # 🚨 Regime Flip Detection & Alerts
            if 'previous_regime' in st.session_state:
                prev = st.session_state.previous_regime
                curr = st.session_state.snapshot['label']
                if prev != curr:
                    msg = f"🔔 *BTC REGIME FLIP DETECTED*\n\n"
                    msg += f"**From**: `{prev}`\n"
                    msg += f"**To**: `{curr}`\n\n"
                    msg += f"Score: {st.session_state.snapshot['score']:.2f}\n"
                    msg += f"Confidence: {st.session_state.snapshot['confidence']}"
                    alert_manager.send_message(msg)
                    st.toast(f"REGIME FLIP: {prev} -> {curr}", icon="🚨")
                    play_regime_flip_audio()
            
            st.session_state.previous_regime = st.session_state.snapshot['label']

    # PAGE LAYOUT (Mobile-Optimized for Telegram)
    from src.ui.dashboard import (
        render_kpi_section, 
        render_macro_thesis, 
        render_component_breakdown,
        render_historical_analysis,
        render_forecast_section,
        render_optimizer_section,
        render_technical_logs
    )

    # Mobile-First: Max 2 columns
    col1, col2 = st.columns([1, 1])

    with col1:
        render_kpi_section(st.session_state.snapshot)

    with col2:
        render_macro_thesis(st.session_state.mtf)
    
    # Component Breakdown (Full Width)
    render_component_breakdown(st.session_state.snapshot['breakdown'])

    # Anomaly Alert Banner
    if 'anomaly_alert' in st.session_state.snapshot:
        alert = st.session_state.snapshot['anomaly_alert']
        if alert['is_anomaly']:
            severity = alert['severity']
            color = "red" if severity == "HIGH" else "orange"
            st.error(f"🚨 **ANOMALY DETECTED**: {severity} SEVERITY MARKET BEHAVIOR", icon="⚠️")
            st.caption(f"Anomaly Score: {alert['anomaly_score']:.4f} | Detection Model: Isolation Forest")

    st.markdown("---")
    
    render_historical_analysis(st.session_state.history, st.session_state.metrics_map)
    
    render_forecast_section(st.session_state.history, st.session_state.snapshot['score'])

    render_optimizer_section(st.session_state.history, st.session_state.metrics_map)

    # Wrap Technical Logs in Expander (Telegram Mobile Optimization)
    with st.expander("🔧 SYSTEM INTERNALS", expanded=False):
        render_technical_logs(st.session_state.metrics_map, st.session_state.snapshot, st.session_state.mtf)

    # Footer
    st.markdown(f"**ENGINE V{st.session_state.snapshot['engine_version']}** | LAST SYNC: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
