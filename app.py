import streamlit as st
import pandas as pd
from datetime import datetime
from src.fetchers import FetcherFactory
from src.analyzer import RegimeAnalyzer, calculate_regime, analyze_history, analyze_mtf
from src.ui.layout import apply_custom_css, inject_google_fonts
from src.ui.charts import plot_regime_history, plot_confluence_heatmap
from src.utils import logger

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

    # PAGE LAYOUT
    col1, col2, col3 = st.columns([1, 1, 1])

    # 1. KPI Cards
    with col1:
        res = st.session_state.snapshot
        label_class = "regime-bull" if res['label'] == "BULL" else "regime-bear" if res['label'] == "BEAR" else "regime-neutral"
        st.markdown(f"### CURRENT REGIME: <span class='{label_class}'>{res['label']}</span>", unsafe_allow_html=True)
        st.metric("Total Score", f"{res['total_score']:.2f}", delta=None)
        st.metric("Confidence", res['confidence'])

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
    st.plotly_chart(plot_regime_history(st.session_state.history), use_container_width=True)

    # Footer
    st.markdown(f"**ENGINE V{st.session_state.snapshot['engine_version']}** | LAST SYNC: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
