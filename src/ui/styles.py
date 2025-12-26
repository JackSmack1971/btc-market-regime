import streamlit as st

def inject_bloomberg_styles():
    """Injects Bloomberg-inspired structural CSS with typographic engineering."""
    st.html("""
        <style>
        /* ========== DYNAMIC SEMANTIC TOKENS ========== */
        :root {
            --finance-green: #4AF6C3;
            --finance-green-rgb: 74, 246, 195;
            --bloomberg-red: #FF433D;
            --trust-blue: #007ACC;
            --structural-border: #3E3E42;
            --background-void: #121212;
            --ui-text-primary: #E0E0E0;
            --ui-text-secondary: rgba(224, 224, 224, 0.6);
        }

        /* ========== TYPOGRAPHIC ENGINEERING ========== */
        
        /* Import JetBrains Mono for all data displays */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');

        /* 1) Global font hierarchy */
        /* Structural Layer: Inter for UI logic */
        html, body, p, div, label, li, .stMarkdown, button, .stButton > button {
            font-family: 'Inter', sans-serif !important;
            font-weight: 400;
        }
        
        /* Ensure Material Symbols are NEVER overridden by Inter */
        /* Structural Headers use Trust Blue */
        h1, h2, h3, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
            color: var(--trust-blue) !important;
            letter-spacing: -0.02em;
            text-transform: uppercase;
        }

        .material-symbols-rounded,
        [data-testid="stExpanderIcon"] {
            font-family: 'Material Symbols Rounded' !important;
        }
        
        /* Hot Path: JetBrains Mono for all market data */
        [data-testid="stMetricValue"], 
        [class*="stDataFrame"], 
        code, 
        .terminal-data, 
        .metric-value,
        .price-value,
        .indicator-value,
        .ticker-tape,
        .order-book-data,
        .health-chip span {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.75rem;
            color: var(--ui-text-secondary);
        }

        /* ========== SENTIMENT COMMAND SUITE ========== */
        .sentiment-feed-container {
            display: flex;
            flex-direction: column;
            gap: 2px;
            margin-top: 10px;
        }

        .sentiment-card {
            background: #1E1E1E !important;
            border-left: 2px solid var(--trust-blue);
            padding: 8px 12px !important;
            margin-bottom: 0px !important;
            transition: all 0.2s ease;
        }

        .sentiment-card:hover {
            background: #252525 !important;
        }

        .sentiment-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
        }

        .sentiment-author {
            font-weight: 700;
            font-size: 0.8rem;
            color: var(--trust-blue);
        }

        .sentiment-time {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            opacity: 0.5;
        }

        .sentiment-body {
            font-size: 0.85rem;
            line-height: 1.3;
            color: var(--ui-text-primary);
        }

        .sentiment-status {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            font-size: 0.75rem;
            margin-top: 4px;
        }
        
        /* Priority Hiding for Sentiment */
        @media (max-width: 600px) {
            .sentiment-body {
                display: none;
            }
            .sentiment-card {
                padding: 4px 8px !important;
            }
        }

        /* 2) Enforce tabular-nums and lining-nums for all numerical displays */
        /* This ensures perfect vertical alignment in tables and prevents layout jitter */
        html, body, * {
            font-variant-numeric: tabular-nums lining-nums !important;
            font-feature-settings: "tnum" 1, "lnum" 1 !important;
            -webkit-font-smoothing: antialiased;
        }

        /* 3) Tri-Layer Hierarchy (Visual Layering) */
        .primary-layer {
            opacity: 1.0 !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }

        .secondary-layer {
            opacity: 1.0 !important;
            font-weight: 600 !important;
        }

        .background-layer {
            opacity: 0.6 !important;
            font-weight: 400 !important;
            color: var(--ui-text-primary) !important;
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
        
        /* ========== BENTO BOX ARCHITECTURE ========== */
        .bento-card {
            background: #1E1E1E !important;
            border: 1px solid var(--structural-border) !important;
            border-radius: 4px !important;
            padding: 12px !important;
            margin-bottom: 8px !important;
            transition: border-color 0.2s ease;
        }

        .bento-card:hover {
            border-color: var(--trust-blue) !important;
        }

        /* Force Zero Padding for Columns (High Density) */
        [data-testid="column"] {
            padding: 0 !important;
        }

        /* Refine Vertical White Space */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
        
        /* Indicators Table Density */
        .indicators-table td {
            padding: 4px 8px !important;
        }

        /* 3) Fixed min-width on metric containers to prevent layout jitter */
        [data-testid="stMetric"] {
            min-width: 200px;
            max-width: 300px;
        }
        
        [data-testid="stMetricValue"] {
            min-width: 140px;
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
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            max-width: 95% !important;
        }
        
        /* Fix sidebar padding for consistency */
        [data-testid="stSidebarNav"] {
            padding-top: 2rem !important;
        }
        
        /* ========== MODULAR BENTO BOX GRID ========== */
        
        /* Eliminate column gaps for high-density widget placement */
        [data-testid='column'] {
            padding: 0 !important;
            gap: 0 !important;
        }
        
        /* Bento Box structural frame - Warm Grey borders */
        .stContainer,
        [data-testid='stVerticalBlock'] > div[data-testid='stVerticalBlock'] {
            border: 1px solid var(--structural-border) !important;
            border-radius: 8px;
            padding: 8px;
            background: rgba(11, 12, 16, 0.6);
            backdrop-filter: blur(4px);
        }
        
        /* Container Queries for Widget Autonomy */
        .bento-widget {
            container-type: inline-size;
            container-name: widget;
        }
        
        /* Widget responsiveness based on container size */
        @container widget (max-width: 300px) {
            .widget-detail {
                display: none;
            }
            .widget-compact {
                display: block;
            }
        }
        
        @container widget (min-width: 301px) {
            .widget-detail {
                display: block;
            }
            .widget-compact {
                display: none;
            }
        }
        
        /* High-Density Metrics Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 8px;
            padding: 4px;
        }
        
        /* 8-Indicator Grid (4 columns on desktop) */
        .indicators-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            padding: 4px;
        }
        
        @media (max-width: 1200px) {
            .indicators-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 600px) {
            .indicators-grid {
                grid-template-columns: 1fr;
            }
        }
        
        /* Data-Ink Optimization: Reduce padding for maximum rows */
        [data-testid="stVerticalBlock"] > div {
            padding: 2px 0;
        }
        
        /* Visual Layering: Labels at 60% opacity */
        [data-testid="stMetricLabel"], .metric-label, .hud-label {
            opacity: 0.6 !important;
            font-weight: 400 !important;
            color: #E0E0E0 !important;
        }

        /* Visual Layering: Primary Data at 100% Bold */
        [data-testid="stMetricValue"], .metric-value, .primary-data {
            opacity: 1.0 !important;
            font-weight: 700 !important;
        }
        
        /* Layout Stability: Fixed widths prevent jitter */
        [data-testid='stMetric'] {
            min-width: 180px;
            max-width: 280px;
            contain: layout;
        }
        
        [data-testid='stMetricValue'] {
            min-width: 120px;
            display: inline-block;
            text-align: right;
        }
        
        /* Priority Hiding Columns */
        .col-priority-1 {
            display: table-cell;
        }
        
        .col-priority-2 {
            display: table-cell;
        }
        
        .col-priority-3 {
            display: table-cell;
        }
        
        /* Large Desktop: Show all (1440px+) */
        
        /* Narrow Desktop/Tablet: Hide Priority 3 (Confidence) */
        @media (max-width: 1440px) {
            .col-priority-3 {
                display: none !important;
            }
        }
        
        /* Mobile/Narrow Tablet: Hide Priority 2 (Raw Value, Secondary Indicators) */
        @media (max-width: 1024px) {
            .col-priority-2,
            .col-priority-3 {
                display: none !important;
            }
        }
        
        /* Ultra-Mobile: Core Execution only (< 600px) */
        @media (max-width: 600px) {
            /* Handled by col-priority logic above */
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
