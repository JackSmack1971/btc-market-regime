import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any

def plot_regime_history(history: List[Dict[str, Any]], prices: pd.DataFrame = None):
    """Generates an interactive Plotly line chart for regime score history with optional price overlay."""
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

    # Price Overlay
    if prices is not None and not prices.empty:
        fig.add_trace(go.Scatter(
            x=prices.index,
            y=prices['close'],
            mode='lines',
            name='BTC Price',
            line=dict(color='rgba(255, 255, 255, 0.4)', width=1, dash='dot'),
            yaxis='y2',
            hovertemplate='Price: $%{y:,.0f}'
        ))
    
    fig.update_layout(
        title="BITCOIN REGIME SCORE HISTORY",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#c9d1d9'),
        xaxis=dict(gridcolor='#30363d', showgrid=True),
        yaxis=dict(title="Score", gridcolor='#30363d', showgrid=True),
        yaxis2=dict(
            title="Price",
            overlaying='y',
            side='right',
            showgrid=False,
            font=dict(color='rgba(255, 255, 255, 0.4)')
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=60, b=0)
    )
    
    return fig

def plot_score_gauge(score: float):
    """Generates a semi-circular gauge for the total regime score."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "REGIME MAGNITUDE", 'font': {'size': 18, 'color': '#c9d1d9'}},
        gauge = {
            'axis': {'range': [-5, 5], 'tickwidth': 1, 'tickcolor': "#30363d"},
            'bar': {'color': "#39FF14" if score > 0 else "#FF3131"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#30363d",
            'steps': [
                {'range': [-5, -1.5], 'color': 'rgba(255, 49, 49, 0.2)'},
                {'range': [-1.5, 1.5], 'color': 'rgba(255, 204, 0, 0.2)'},
                {'range': [1.5, 5], 'color': 'rgba(57, 255, 20, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#c9d1d9'),
        height=250,
        margin=dict(l=20, r=20, t=50, b=20)
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
