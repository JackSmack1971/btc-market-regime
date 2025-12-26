import streamlit as st

def inject_bloomberg_styles():
    """Injects Bloomberg-inspired structural CSS with typographic engineering."""
    st.html("""
        <style>
        /* ========== TYPOGRAPHIC ENGINEERING ========== */
        
        /* Import JetBrains Mono for all data displays */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');

        /* 1) Global font hierarchy */
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Apply JetBrains Mono to all data containers */
        [data-testid="stMetricValue"], 
        [class*="stDataFrame"], 
        code, 
        .terminal-data, 
        .metric-value,
        .price-value,
        .indicator-value {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* 2) Enforce tabular-nums and lining-nums for all numerical displays */
        /* This ensures perfect vertical alignment in tables and prevents layout jitter */
        * {
            font-variant-numeric: tabular-nums lining-nums;
            font-feature-settings: "tnum" 1, "lnum" 1;
        }

        /* Target specific Streamlit elements for tabular alignment */
        [data-testid="stMetricValue"], 
        [data-testid="stTable"], 
        .stDataFrame, 
        .stText,
        .price-value,
        .indicator-value {
            font-variant-numeric: tabular-nums lining-nums !important;
            font-feature-settings: "tnum" 1, "lnum" 1 !important;
        }
        
        /* 3) Fixed min-width on metric containers to prevent layout jitter */
        [data-testid="stMetric"] {
            min-width: 180px;
            max-width: 280px;
        }
        
        [data-testid="stMetricValue"] {
            min-width: 120px;
            display: inline-block;
            text-align: right;
        }
        
        /* Price columns get extra stability */
        .price-value {
            min-width: 140px;
            display: inline-block;
            text-align: right;
        }
        
        /* Indicator values */
        .indicator-value {
            min-width: 100px;
            display: inline-block;
            text-align: right;
        }

        /* ========== STRUCTURAL LAYOUT ========== */
        
        /* Remove default 6rem top padding from .block-container */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 95% !important;
        }
        
        /* Fix sidebar padding for consistency */
        [data-testid="stSidebarNav"] {
            padding-top: 2rem !important;
        }
        
        /* ========== FLASH EFFECTS ON UPDATES ========== */
        
        /* 200ms flash effect for price/value updates */
        @keyframes value-flash {
            0% {
                background-color: rgba(5, 217, 232, 0);
            }
            50% {
                background-color: rgba(5, 217, 232, 0.2);
            }
            100% {
                background-color: rgba(5, 217, 232, 0);
            }
        }
        
        /* Apply flash to metric values on update */
        [data-testid="stMetricValue"].flash-update,
        .price-value.flash-update,
        .indicator-value.flash-update {
            animation: value-flash 200ms ease-out;
        }
        
        /* Alternative flash for positive changes */
        @keyframes value-flash-positive {
            0% {
                background-color: rgba(74, 246, 195, 0);
            }
            50% {
                background-color: rgba(74, 246, 195, 0.2);
            }
            100% {
                background-color: rgba(74, 246, 195, 0);
            }
        }
        
        .flash-positive {
            animation: value-flash-positive 200ms ease-out;
        }
        
        /* Alternative flash for negative changes */
        @keyframes value-flash-negative {
            0% {
                background-color: rgba(255, 67, 61, 0);
            }
            50% {
                background-color: rgba(255, 67, 61, 0.2);
            }
            100% {
                background-color: rgba(255, 67, 61, 0);
            }
        }
        
        .flash-negative {
            animation: value-flash-negative 200ms ease-out;
        }
        
        /* ========== ANTI-JITTER ENGINEERING ========== */
        
        /* Prevent layout shift during content updates */
        .stMetric, [data-testid="stMetric"] {
            contain: layout;
            will-change: contents;
        }
        
        /* Stabilize table columns */
        .indicators-table td,
        .backtest-table td {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        /* Fixed-width columns for price data */
        .col-price {
            width: 140px;
            min-width: 140px;
            max-width: 140px;
        }
        
        .col-score {
            width: 100px;
            min-width: 100px;
            max-width: 100px;
        }
        
        .col-confidence {
            width: 120px;
            min-width: 120px;
            max-width: 120px;
        }
        
        /* ========== PERFORMANCE OPTIMIZATIONS ========== */
        
        /* Use GPU acceleration for animations */
        .flash-update,
        .flash-positive,
        .flash-negative {
            transform: translateZ(0);
            backface-visibility: hidden;
        }
        
        /* Optimize font rendering */
        body {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }
        
        /* Prevent FOUT (Flash of Unstyled Text) */
        .wf-loading {
            visibility: hidden;
        }
        
        .wf-active {
            visibility: visible;
        }
        </style>
    """)
