import streamlit as st

def inject_terminal_fonts():
    """Loads Terminal Aesthetics typography: Orbitron, JetBrains Mono, Inter."""
    st.markdown('''
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    ''', unsafe_allow_html=True)
