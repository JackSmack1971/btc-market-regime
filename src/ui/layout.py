import streamlit as st

def apply_custom_css():
    """Injects the Cyber-Noir Design System CSS."""
    st.markdown("""
        <style>
        /* Main Background */
        .stApp {
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        /* Glassmorphism Cards */
        [data-testid="stMetric"] {
            background: rgba(22, 27, 34, 0.7);
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Neon Accents for Regimes */
        .regime-bull { color: #39FF14; text-shadow: 0 0 10px #39FF14; font-weight: bold; }
        .regime-bear { color: #FF3131; text-shadow: 0 0 10px #FF3131; font-weight: bold; }
        .regime-neutral { color: #FFCC00; text-shadow: 0 0 10px #FFCC00; font-weight: bold; }
        
        /* Sidebar Polish */
        [data-testid="stSidebar"] {
            background-color: #161b22;
            border-right: 1px solid #30363d;
        }
        
        /* Tactical Typography */
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Table Styling */
        .stDataFrame {
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

def inject_google_fonts():
    st.markdown('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">', unsafe_allow_html=True)
