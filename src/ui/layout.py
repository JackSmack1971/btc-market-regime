import streamlit as st

def apply_custom_css():
    """Injects the Cyber-Noir Design System CSS."""
    st.markdown("""
        <style>
        /* ========== TERMINAL AESTHETICS: DESIGN TOKENS ========== */
        :root {
            /* Deep Gunmetal Gradient Palette */
            --terminal-bg-deep: #06080b;
            --terminal-bg-mid: #0e1117;
            --terminal-bg-surface: #1f2833;
            --terminal-glass: rgba(31, 40, 51, 0.4);
            --terminal-glass-hover: rgba(31, 40, 51, 0.7);
            
            /* Neon Cyber Palette */
            --neon-cyber-green: #00FF9D;
            --neon-radical-red: #FF2A6D;
            --neon-electric-blue: #05D9E8;
            --neon-amber: #FFD60A;
            
            /* Terminal Text Colors */
            --terminal-text-primary: #c5c6c7;
            --terminal-text-secondary: #66fcf1;
            --terminal-text-muted: #45a29e;
            --terminal-text-dim: #1f2833;
            
            /* Spacing (8px grid) */
            --space-xs: 0.5rem;
            --space-sm: 0.75rem;
            --space-md: 1rem;
            --space-lg: 1.5rem;
            --space-xl: 2rem;
            
            /* Border & Radius */
            --terminal-border: 1px solid #45a29e;
            --terminal-border-neon: 1px solid var(--neon-cyber-green);
            --radius-sharp: 3px;
            --radius-pill: 20px;
            
            /* Shadows & Glows */
            --glow-cyber-green: 0 0 10px rgba(0, 255, 157, 0.3), 0 0 20px rgba(0, 255, 157, 0.1);
            --glow-radical-red: 0 0 10px rgba(255, 42, 109, 0.3), 0 0 20px rgba(255, 42, 109, 0.1);
            --glow-electric-blue: 0 0 10px rgba(5, 217, 232, 0.3), 0 0 20px rgba(5, 217, 232, 0.1);
            --shadow-terminal: 0 4px 20px rgba(0, 0, 0, 0.5);
            
            /* Typography */
            --font-heading: 'Orbitron', 'Inter', sans-serif;
            --font-data: 'JetBrains Mono', 'Courier New', monospace;
            --font-body: 'Inter', -apple-system, sans-serif;
            
            /* Transitions */
            --transition-fast: 0.15s ease-out;
            --transition-base: 0.3s ease-out;
        }
        
        /* ========== GLOBAL TERMINAL BACKGROUND ========== */
        .stApp {
            background-color: var(--terminal-bg-deep);
            background-image: radial-gradient(circle at 50% 0%, var(--terminal-bg-mid) 0%, var(--terminal-bg-deep) 70%);
            color: var(--terminal-text-primary);
            font-family: var(--font-body);
        }
        
        /* ========== TERMINAL TYPOGRAPHY ========== */
        h1, h2, h3 {
            font-family: var(--font-heading);
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: var(--terminal-text-secondary);
            text-shadow: var(--glow-electric-blue);
            font-weight: 700;
        }
        
        h1 {
            font-size: 1.75rem;
            margin-bottom: var(--space-lg);
        }
        
        h2 {
            font-size: 1.25rem;
            margin-top: var(--space-xl);
            margin-bottom: var(--space-md);
        }
        
        h3 {
            font-size: 1rem;
            color: var(--terminal-text-muted);
            text-shadow: none;
        }
        
        /* Data/Numbers: Monospace */
        [data-testid="stMetricValue"],
        .metric-value,
        .terminal-data {
            font-family: var(--font-data) !important;
            font-weight: 600;
            letter-spacing: 0.05em;
        }
        
        /* ========== GLASSMORPHISM METRIC CARDS ========== */
        [data-testid="stMetric"] {
            background: var(--terminal-glass);
            border: var(--terminal-border);
            border-radius: var(--radius-sharp);
            padding: var(--space-lg);
            box-shadow: var(--shadow-terminal), inset 0 1px 0 rgba(102, 252, 241, 0.1);
            backdrop-filter: blur(10px);
            transition: all var(--transition-base);
        }
        
        [data-testid="stMetric"]:hover {
            background: var(--terminal-glass-hover);
            border-color: var(--neon-cyber-green);
            box-shadow: var(--glow-cyber-green), var(--shadow-terminal);
            transform: translateY(-2px);
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            color: var(--neon-electric-blue);
            text-shadow: var(--glow-electric-blue);
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.75rem;
            color: var(--terminal-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-family: var(--font-heading);
        }
        
        /* ========== REGIME INDICATORS (NEON PILLS) ========== */
        .regime-bull {
            display: inline-block;
            padding: var(--space-xs) var(--space-lg);
            background: rgba(0, 255, 157, 0.1);
            border: 2px solid var(--neon-cyber-green);
            border-radius: var(--radius-pill);
            color: var(--neon-cyber-green);
            font-family: var(--font-heading);
            font-weight: 900;
            font-size: 1.25rem;
            letter-spacing: 0.2em;
            text-shadow: var(--glow-cyber-green);
            box-shadow: var(--glow-cyber-green);
        }
        
        .regime-bear {
            display: inline-block;
            padding: var(--space-xs) var(--space-lg);
            background: rgba(255, 42, 109, 0.1);
            border: 2px solid var(--neon-radical-red);
            border-radius: var(--radius-pill);
            color: var(--neon-radical-red);
            font-family: var(--font-heading);
            font-weight: 900;
            font-size: 1.25rem;
            letter-spacing: 0.2em;
            text-shadow: var(--glow-radical-red);
            box-shadow: var(--glow-radical-red);
        }
        
        .regime-neutral {
            display: inline-block;
            padding: var(--space-xs) var(--space-lg);
            background: rgba(255, 214, 10, 0.1);
            border: 2px solid var(--neon-amber);
            border-radius: var(--radius-pill);
            color: var(--neon-amber);
            font-family: var(--font-heading);
            font-weight: 900;
            font-size: 1.25rem;
            letter-spacing: 0.2em;
            text-shadow: 0 0 10px rgba(255, 214, 10, 0.5);
            box-shadow: 0 0 10px rgba(255, 214, 10, 0.3);
        }
        
        /* ========== SIDEBAR: COMMAND LINK ========== */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--terminal-bg-mid) 0%, var(--terminal-bg-deep) 100%);
            border-right: 2px solid var(--terminal-text-muted);
        }
        
        [data-testid="stSidebar"] h2 {
            color: var(--neon-electric-blue);
            font-family: var(--font-heading);
            font-size: 0.9rem;
            letter-spacing: 0.2em;
        }
        
        /* ========== TACTICAL BUTTONS ========== */
        .stButton > button {
            background: linear-gradient(135deg, rgba(0, 255, 157, 0.2) 0%, rgba(0, 255, 157, 0.1) 100%);
            color: var(--neon-cyber-green);
            border: 2px solid var(--neon-cyber-green);
            border-radius: var(--radius-sharp);
            padding: var(--space-md) var(--space-xl);
            font-family: var(--font-heading);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            transition: all var(--transition-base);
            box-shadow: var(--glow-cyber-green);
            min-height: 44px; /* Mobile touch target */
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, rgba(0, 255, 157, 0.3) 0%, rgba(0, 255, 157, 0.2) 100%);
            box-shadow: 0 0 20px rgba(0, 255, 157, 0.5), 0 0 40px rgba(0, 255, 157, 0.2);
            transform: translateY(-2px);
            border-color: var(--neon-cyber-green);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* ========== TABLES: KILL THE DATAFRAME LOOK ========== */
        .stDataFrame {
            background: var(--terminal-glass);
            border: var(--terminal-border);
            border-radius: var(--radius-sharp);
            overflow: hidden;
            box-shadow: var(--shadow-terminal);
            font-family: var(--font-data);
        }
        
        .stDataFrame thead tr th {
            background: rgba(5, 217, 232, 0.1) !important;
            color: var(--neon-electric-blue) !important;
            font-family: var(--font-heading) !important;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-size: 0.75rem;
            padding: var(--space-sm) !important;
            border-bottom: 2px solid var(--neon-electric-blue) !important;
        }
        
        .stDataFrame tbody tr {
            background: rgba(11, 12, 16, 0.6);
            transition: background var(--transition-fast);
        }
        
        .stDataFrame tbody tr:hover {
            background: var(--terminal-glass);
        }
        
        .stDataFrame tbody tr td {
            padding: var(--space-xs) var(--space-sm) !important;
            border-bottom: 1px solid rgba(69, 162, 158, 0.2) !important;
            color: var(--terminal-text-primary);
            font-size: 0.9rem;
        }
        
        /* ========== EXPANDERS: SYSTEM INTERNALS ========== */
        .streamlit-expanderHeader {
            background: var(--terminal-glass);
            border: var(--terminal-border);
            border-radius: var(--radius-sharp);
            font-family: var(--font-heading);
            font-weight: 600;
            letter-spacing: 0.1em;
            color: var(--terminal-text-muted);
            transition: all var(--transition-fast);
        }
        
        .streamlit-expanderHeader:hover {
            background: var(--terminal-glass-hover);
            border-color: var(--neon-electric-blue);
            color: var(--neon-electric-blue);
        }
        
        /* ========== DIVIDERS ========== */
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, 
                transparent 0%, 
                var(--terminal-text-muted) 50%, 
                transparent 100%);
            margin: var(--space-xl) 0;
        }
        
        /* ========== LIVE CONNECTION BEACON ========== */
        @keyframes pulse-beacon {
            0%, 100% { 
                opacity: 1; 
                box-shadow: 0 0 5px var(--neon-cyber-green), 0 0 10px var(--neon-cyber-green);
            }
            50% { 
                opacity: 0.6; 
                box-shadow: 0 0 10px var(--neon-cyber-green), 0 0 20px var(--neon-cyber-green);
            }
        }
        
        .live-beacon {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: var(--neon-cyber-green);
            border-radius: 50%;
            animation: pulse-beacon 2s infinite;
            margin-right: var(--space-xs);
        }
        
        /* ========== MOBILE OPTIMIZATION (TELEGRAM) ========== */
        @media (max-width: 768px) {
            h1 {
                font-size: 1.25rem;
                letter-spacing: 0.1em;
            }
            
            [data-testid="stMetric"] {
                padding: var(--space-md);
            }
            
            [data-testid="stMetricValue"] {
                font-size: 1.5rem;
            }
            
            .regime-bull, .regime-bear, .regime-neutral {
                font-size: 1rem;
                padding: var(--space-xs) var(--space-md);
            }
            
            .stButton > button {
                width: 100%;
                padding: var(--space-md);
            }
        }
        
        /* ========== ACCESSIBILITY ========== */
        *:focus-visible {
            outline: 2px solid var(--neon-electric-blue);
            outline-offset: 2px;
        }
        
        /* ========== LOADING STATES ========== */
        .stSpinner > div {
            border-color: var(--neon-electric-blue) transparent transparent transparent !important;
        }
        
        /* ========== TOAST NOTIFICATIONS ========== */
        .stToast {
            background: var(--terminal-glass) !important;
            border: var(--terminal-border-neon) !important;
            border-radius: var(--radius-sharp) !important;
            box-shadow: var(--glow-cyber-green), var(--shadow-terminal) !important;
            font-family: var(--font-data) !important;
        }
        
        /* ========== CUSTOM HUD GRID (replaces dataframes) ========== */
        .hud-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--space-md);
            margin: var(--space-lg) 0;
        }
        
        .hud-card {
            background: var(--terminal-glass);
            border: var(--terminal-border);
            border-radius: var(--radius-sharp);
            padding: var(--space-md);
            transition: all var(--transition-fast);
        }
        
        .hud-card:hover {
            border-color: var(--neon-cyber-green);
            box-shadow: var(--glow-cyber-green);
        }
        
        .hud-label {
            font-family: var(--font-heading);
            font-size: 0.7rem;
            color: var(--terminal-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: var(--space-xs);
        }
        
        .hud-value {
            font-family: var(--font-data);
            font-size: 1.25rem;
            color: var(--neon-electric-blue);
            font-weight: 700;
        }
        
        /* ========== SYSTEM HEALTH CHIPS ========== */
        .health-chip {
            display: inline-flex;
            align-items: center;
            gap: var(--space-xs);
            padding: var(--space-xs) var(--space-sm);
            background: var(--terminal-glass);
            border: var(--terminal-border);
            border-radius: var(--radius-sharp);
            font-family: var(--font-data);
            font-size: 0.75rem;
            margin-right: var(--space-xs);
            margin-bottom: var(--space-xs);
        }
        
        .health-dot-success {
            width: 8px;
            height: 8px;
            background: var(--neon-cyber-green);
            border-radius: 50%;
            box-shadow: 0 0 5px var(--neon-cyber-green);
        }
        
        .health-dot-failure {
            width: 8px;
            height: 8px;
            background: var(--neon-radical-red);
            border-radius: 50%;
            box-shadow: 0 0 5px var(--neon-radical-red);
            animation: pulse-beacon 1s infinite;
        }
        </style>
    """, unsafe_allow_html=True)

def inject_google_fonts():
    """Legacy function - now loads Terminal Aesthetics typography."""
    from .terminal_fonts import inject_terminal_fonts
    inject_terminal_fonts()
