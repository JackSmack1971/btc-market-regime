import streamlit as st

def inject_bloomberg_styles():
    """Injects Bloomberg-inspired structural CSS via st.html."""
    # Note: Using st.html as requested. In newer Streamlit, this is preferred for static HTML/CSS.
    st.html("""
        <style>
        /* Import fonts if not already globally loaded */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');

        /* 1) Set global fonts */
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Apply monospace to specific data containers */
        [data-testid="stMetricValue"], 
        [class*="stDataFrame"], 
        code, 
        .terminal-data, 
        .metric-value {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* 2) Remove default 6rem top padding from .block-container */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 95% !important;
        }
        
        /* 3) Enforce 'tnum' (tabular numbers) for all numerical displays */
        /* This ensures numbers align vertically in tables and lists */
        * {
            font-variant-numeric: tabular-nums;
            font-feature-settings: "tnum" 1;
        }

        /* Target specific Streamlit elements for tabular alignment */
        [data-testid="stMetricValue"], 
        [data-testid="stTable"], 
        .stDataFrame, 
        .stText {
            font-feature-settings: "tnum" 1 !important;
        }
        
        /* Fix sidebar padding as well for consistency */
        [data-testid="stSidebarNav"] {
            padding-top: 2rem !important;
        }
        </style>
    """)
