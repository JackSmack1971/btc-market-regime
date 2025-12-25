import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any

def plot_regime_history(history: List[Dict[str, Any]]):
    """Generates an interactive Plotly line chart for regime score history."""
    df = pd.DataFrame(history)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    fig = go.Figure()

    # Total Score Line
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['total_score'],
        mode='lines+markers',
        name='Regime Score',
        line=dict(color='#39FF14', width=2),
        marker=dict(size=6),
        hovertemplate='Date: %{x}<br>Score: %{y}<br>Regime: %{text}',
        text=df['label']
    ))

    # Add background shapes for regimes
    # (Simplified for now - can add shaded regions per label later)
    
    fig.update_layout(
        title="BITCOIN REGIME SCORE HISTORY",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#c9d1d9'),
        xaxis=dict(gridcolor='#30363d', showgrid=True),
        yaxis=dict(gridcolor='#30363d', showgrid=True),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig

def plot_confluence_heatmap(mtf_results: Dict[str, Any]):
    """Generates a visual 'Confluence Bar' for Daily/Weekly/Monthly alignment."""
    horizons = ['daily', 'weekly', 'monthly']
    labels = [mtf_results[h]['label'] for h in horizons]
    scores = [mtf_results[h]['total_score'] for h in horizons]
    
    # Map labels to colors
    colors = []
    for l in labels:
        if l == "BULL": colors.append("#39FF14")
        elif l == "BEAR": colors.append("#FF3131")
        else: colors.append("#FFCC00")

    fig = go.Figure(go.Bar(
        x=[h.upper() for h in horizons],
        y=scores,
        marker_color=colors,
        text=labels,
        textposition='auto',
    ))

    fig.update_layout(
        title="MULTI-TIMEFRAME CONFLUENCE",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#c9d1d9'),
        xaxis=dict(gridcolor='#30363d'),
        yaxis=dict(gridcolor='#30363d'),
        margin=dict(l=0, r=0, t=40, b=0)
    )

    return fig
