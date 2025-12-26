import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from .charts import plot_regime_history, plot_confluence_heatmap, plot_score_gauge
from ..intelligence.forecaster import RegimeForecaster
from ..backtesting.optimizer import BacktestOptimizer

def render_kpi_section(snapshot: Dict[str, Any]):
    """Renders the top KPI cards with Visual Layering and high-frequency regime verdict updates."""
    
    # High-frequency fragment for Market Regime Verdict (10Hz updates)
    @st.fragment(run_every="0.1s")
    def render_regime_verdict():
        """Auto-refreshing regime verdict with flash effect on state change."""
        current_snapshot = st.session_state.get('snapshot', snapshot)
        label = current_snapshot.get('label', 'UNKNOWN')
        score = current_snapshot.get('score', 0.0)
        confidence = current_snapshot.get('confidence', 'UNKNOWN')
        
        # Detect state change for flash effect
        prev_label = st.session_state.get('prev_regime_label', label)
        flash_class = "flash-regime" if prev_label != label else ""
        st.session_state.prev_regime_label = label
        
        label_class = "regime-bull" if label == "BULL" else "regime-bear" if label == "BEAR" else "regime-neutral"
        
        # Visual Layering: Raw HTML with semantic colors and flash effect
        html = f"""
        <style>
        /* Flash effect on regime state change (300ms) */
        @keyframes flash-regime {{
            0% {{ background-color: rgba(5, 217, 232, 0); }}
            50% {{ background-color: rgba(5, 217, 232, 0.3); }}
            100% {{ background-color: rgba(5, 217, 232, 0); }}
        }}
        
        .regime-verdict-container {{
            margin-bottom: 1.5rem;
            padding: 1rem;
            border-radius: 8px;
        }}
        
        .regime-verdict-container.flash-regime {{
            animation: flash-regime 300ms ease-out;
        }}
        
        /* Visual Layering: Label at 60% opacity */
        .regime-verdict-title {{
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            font-weight: 400;
            color: rgba(255, 255, 255, 0.6);
            opacity: 0.6;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.5rem;
        }}
        
        /* Visual Layering: Value at 100% opacity, 700 weight */
        .regime-verdict-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 2rem;
            font-weight: 700;
            opacity: 1.0;
            margin: 0;
        }}
        </style>
        <div class="regime-verdict-container {flash_class}">
            <div class="regime-verdict-title background-layer">CURRENT REGIME:</div>
            <h3 class="regime-verdict-value primary-layer"><span class="{label_class}">{label}</span></h3>
        </div>
        """
        st.html(html)
    
    # Render high-frequency regime verdict
    render_regime_verdict()
    
    # Visual Layering for metrics: values at opacity 1.0, labels at 0.6
    score = snapshot['score']
    confidence = snapshot['confidence']
    
    st.html(f"""
        <style>
        /* Visual Layering for metric cards */
        [data-testid="stMetricLabel"] {{
            opacity: 0.6 !important;
            font-weight: 400 !important;
        }}
        
        [data-testid="stMetricValue"] {{
            opacity: 1.0 !important;
            font-weight: 700 !important;
        }}
        
        /* Semantic colors for score value */
        .score-positive {{
            color: #4AF6C3 !important;
        }}
        
        .score-negative {{
            color: #FF433D !important;
        }}
        </style>
    """)
    
    st.metric("Total Score", f"{score:.2f}", help="Aggregated score from -5 to +5.")
    st.metric("Confidence", confidence, help="Reliability of the current signal.")
    
    st.plotly_chart(plot_score_gauge(score), use_container_width=True)

def render_macro_thesis(mtf: Dict[str, Any]):
    """Renders the macro thesis text and confluence heatmap."""
    st.markdown("### MACRO THESIS")
    st.info(mtf['macro_thesis'])
    st.plotly_chart(plot_confluence_heatmap(mtf), use_container_width=True)

def render_component_breakdown(breakdown: List[Dict[str, Any]]):
    """
    Renders the individual indicator breakdown table with high-frequency auto-refresh.
    Uses Bento Box 4-column grid for high-density display.
    """
    if not breakdown:
        st.info("No indicator data available yet.")
        return
    
    st.markdown("### 📊 COMPONENT BREAKDOWN")
    
    # High-frequency fragment for auto-refresh (0.5s synchronization)
    @st.fragment(run_every="0.5s")
    def render_indicators_table():
        """Auto-refreshing HTML table for Top 8 Indicators."""
        html = """
        <style>
        .indicators-table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(31, 40, 51, 0.4);
            border: 1px solid #45a29e;
            border-radius: 3px;
            overflow: hidden;
            font-feature-settings: "tnum" 1, "lnum" 1;
            font-variant-numeric: tabular-nums lining-nums;
            table-layout: fixed;
        }
        
        .indicators-table thead {
            background: rgba(var(--finance-green-rgb), 0.1);
        }
        
        .indicators-table th {
            padding: 12px 16px;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 0.75rem;
        color: var(--finance-green);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        border-bottom: 2px solid var(--finance-green);
        vertical-align: middle;
    }
        
        .indicators-table th:nth-child(1) {
            width: 40%;
            text-align: left;
        }
        
        .indicators-table th:nth-child(2),
        .indicators-table th:nth-child(3),
        .indicators-table th:nth-child(4) {
            width: 20%;
            min-width: 120px;
            max-width: 120px;
            text-align: right;
        }
        
        .indicators-table tbody tr {
            background: rgba(11, 12, 16, 0.6);
            transition: background 0.15s ease-out;
        }
        
        .indicators-table tbody tr:hover {
            background: rgba(31, 40, 51, 0.7);
        }
        
        .indicators-table td {
            padding: 10px 16px;
            border-bottom: 1px solid rgba(69, 162, 158, 0.2);
            vertical-align: middle;
            white-space: nowrap;
        }
        
        /* Label Column: Inter Regular 60% grey */
        .indicator-label {
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.6);
            text-align: left;
        }
        
        /* Value Columns: JetBrains Mono Bold 100% white */
        .indicator-value {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            font-size: 0.95rem;
            color: rgba(255, 255, 255, 1.0);
            text-align: right;
        }
        
        /* Momentum Signals: Finance Green / Bloomberg Red */
        .momentum-positive {
            color: var(--finance-green);
            text-shadow: 0 0 8px rgba(74, 246, 195, 0.4);
        }
        
        .momentum-negative {
            color: var(--bloomberg-red);
            text-shadow: 0 0 8px rgba(255, 67, 61, 0.4);
        }
        
        .momentum-neutral {
            color: var(--ui-text-secondary);
        }
        
        /* Confidence Badge */
        .confidence-high {
            color: var(--finance-green);
            font-weight: 600;
        }
        
        .confidence-medium {
            color: #FFD60A;
            font-weight: 600;
        }
        
        .confidence-low {
            color: var(--bloomberg-red);
            font-weight: 600;
        }
        </style>
        
        <table class="indicators-table">
            <thead>
                <tr>
                    <th class="col-priority-1">INDICATOR</th>
                    <th class="col-priority-1">SCORE</th>
                    <th class="col-priority-2">RAW VALUE</th>
                    <th class="col-priority-3">CONFIDENCE</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for indicator in breakdown[:8]:  # Top 8 indicators
            metric_name = indicator.get('metric_name', 'Unknown')
            score = indicator.get('score', 0.0)
            raw_value = indicator.get('raw_value', 0.0)
            confidence = indicator.get('confidence', 'UNKNOWN')
            
            # Determine momentum class based on score
            if score > 0.5:
                momentum_class = "momentum-positive"
                momentum_symbol = "▲"
            elif score < -0.5:
                momentum_class = "momentum-negative"
                momentum_symbol = "▼"
            else:
                momentum_class = "momentum-neutral"
                momentum_symbol = "●"
            
            # Confidence styling
            if confidence == "HIGH":
                confidence_class = "confidence-high"
            elif confidence == "MEDIUM":
                confidence_class = "confidence-medium"
            else:
                confidence_class = "confidence-low"
            
            # Format raw value
            if isinstance(raw_value, (int, float)):
                if abs(raw_value) >= 1000:
                    raw_value_str = f"{raw_value:,.0f}"
                else:
                    raw_value_str = f"{raw_value:.2f}"
            else:
                raw_value_str = str(raw_value)

            # Priority Hiding Logic: Hide secondary columns on mobile
            low_priority_metrics = ["Network Hash Rate", "Exchange Net Flows"]
            priority_class = "col-priority-2" if metric_name in low_priority_metrics else "col-priority-1"
            
            # CRITICAL FIX: Column order must match header order
            # Header: INDICATOR | SCORE | RAW VALUE | CONFIDENCE
            html += f"""
                <tr class="{priority_class}">
                    <td class="indicator-label background-layer col-priority-1">{metric_name}</td>
                    <td class="indicator-value primary-layer {momentum_class} col-priority-1">{momentum_symbol} {score:.2f}</td>
                    <td class="indicator-value secondary-layer col-priority-2">{raw_value_str}</td>
                    <td class="indicator-value background-layer {confidence_class} col-priority-3">{confidence}</td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        """
        
        st.html(html)
    
    # Render the auto-refreshing fragment
    render_indicators_table()

def render_historical_analysis(history: List[Dict[str, Any]], metrics_map: Dict[str, Any]):
    """Renders the historical regime chart with price overlay."""
    btc_prices = pd.DataFrame()
    if 'binance' in metrics_map:
        data = metrics_map['binance']
        btc_prices = pd.DataFrame([data] if isinstance(data, dict) else data)
        if not btc_prices.empty and 'timestamp' in btc_prices.columns:
            btc_prices.set_index('timestamp', inplace=True)
    elif 'coingecko' in metrics_map:
        data = metrics_map['coingecko']
        btc_prices = pd.DataFrame([data] if isinstance(data, dict) else data)
        if not btc_prices.empty and 'timestamp' in btc_prices.columns:
            btc_prices.set_index('timestamp', inplace=True)

    st.plotly_chart(plot_regime_history(history, btc_prices), use_container_width=True)

def render_forecast_section(history: List[Dict[str, Any]], current_score: float):
    """Renders the experimental forecast engine."""
    if not history:
         st.info("🔮 Forecast engine requires historical data.")
         return

    forecaster = RegimeForecaster(history)
    forecaster.train()
    
    if forecaster.is_trained:
        st.markdown("### 🔮 EXPERIMENTAL FORECAST (Next 12 Hours)")
        forecasts = forecaster.forecast(current_score)
        forecast_df = pd.DataFrame(forecasts)
        st.line_chart(forecast_df.set_index('timestamp'), y='projected_score')
        st.caption("Forecast model: Linear Regression Projection (Experimental)")
    else:
        st.info("🔮 Forecast engine warming up. Accumulating more data...")

def render_optimizer_section(history: List[Dict[str, Any]], metrics_map: Dict[str, Any]):
    """Renders the strategy weight optimizer."""
    with st.expander("🧪 STRATEGY OPTIMIZER (EXPERIMENTAL)"):
        if not history:
            st.info("Optimization requires active session history.")
            return

        st.markdown("Find the optimal mathematical weights for your metrics using Bayesian optimization.")
        
        # Track previous regime for flash effect
        if 'previous_regime_verdict' not in st.session_state:
            st.session_state.previous_regime_verdict = None
        
        # Slide-to-Confirm Component for Backtest Execution
        st.html("""
            <style>
            .slide-to-confirm-container {
                width: 100%;
                margin: 1rem 0;
            }
            
            .slide-track {
                position: relative;
                width: 100%;
                height: 60px;
                background: rgba(31, 40, 51, 0.6);
                border: 2px solid #45a29e;
                border-radius: 30px;
                overflow: hidden;
                cursor: pointer;
                user-select: none;
            }
            
            .slide-background {
                position: absolute;
                left: 0;
                top: 0;
                height: 100%;
                width: 0%;
                background: linear-gradient(90deg, #4AF6C3 0%, #05D9E8 100%);
                transition: width 0.3s ease-out;
                border-radius: 30px;
            }
            
            .slide-button {
                position: absolute;
                left: 4px;
                top: 4px;
                width: 52px;
                height: 52px;
                background: linear-gradient(135deg, #4AF6C3 0%, #05D9E8 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                box-shadow: 0 4px 12px rgba(74, 246, 195, 0.4);
                transition: left 0.3s ease-out;
                z-index: 10;
            }
            
            .slide-text {
                position: absolute;
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Inter', sans-serif;
                font-weight: 600;
                font-size: 0.9rem;
                color: rgba(255, 255, 255, 0.8);
                text-transform: uppercase;
                letter-spacing: 0.1em;
                pointer-events: none;
                z-index: 5;
            }
            
            .slide-track.confirmed .slide-background {
                width: 100%;
            }
            
            .slide-track.confirmed .slide-button {
                left: calc(100% - 56px);
            }
            
            .slide-track.confirmed .slide-text {
                color: rgba(11, 12, 16, 0.9);
            }
            </style>
            
            <div class="slide-to-confirm-container">
                <div class="slide-track" id="slideTrack">
                    <div class="slide-background"></div>
                    <div class="slide-button">▶</div>
                    <div class="slide-text">SLIDE TO RUN INSTITUTIONAL BACKTEST</div>
                </div>
            </div>
            
            <script>
            (function() {
                const track = document.getElementById('slideTrack');
                const button = track.querySelector('.slide-button');
                const background = track.querySelector('.slide-background');
                const text = track.querySelector('.slide-text');
                
                let isDragging = false;
                let startX = 0;
                let currentX = 0;
                const maxDistance = track.offsetWidth - 60;
                
                function handleStart(e) {
                    isDragging = true;
                    startX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
                    track.style.cursor = 'grabbing';
                }
                
                function handleMove(e) {
                    if (!isDragging) return;
                    
                    const clientX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
                    currentX = Math.max(0, Math.min(maxDistance, clientX - startX));
                    
                    const percentage = (currentX / maxDistance) * 100;
                    button.style.left = currentX + 4 + 'px';
                    background.style.width = percentage + '%';
                    
                    // Change text opacity as user slides
                    text.style.opacity = 1 - (percentage / 100);
                }
                
                function handleEnd() {
                    if (!isDragging) return;
                    isDragging = false;
                    track.style.cursor = 'pointer';
                    
                    // Check if slid past 80% threshold
                    if (currentX > maxDistance * 0.8) {
                        // Confirmed! Trigger optimization
                        track.classList.add('confirmed');
                        text.textContent = 'OPTIMIZATION STARTED';
                        
                        // Trigger Streamlit rerun with optimization flag
                        setTimeout(() => {
                            window.parent.postMessage({
                                type: 'streamlit:setComponentValue',
                                value: true
                            }, '*');
                        }, 300);
                    } else {
                        // Reset
                        button.style.left = '4px';
                        background.style.width = '0%';
                        text.style.opacity = '1';
                    }
                    
                    currentX = 0;
                }
                
                // Mouse events
                button.addEventListener('mousedown', handleStart);
                document.addEventListener('mousemove', handleMove);
                document.addEventListener('mouseup', handleEnd);
                
                // Touch events
                button.addEventListener('touchstart', handleStart);
                document.addEventListener('touchmove', handleMove);
                document.addEventListener('touchend', handleEnd);
            })();
            </script>
        """)
        
        # Check if slide-to-confirm was triggered (fallback to button for now)
        if st.button("RUN WEIGHT OPTIMIZATION", use_container_width=True, key="backup_optimizer_button"):
            from ..backtesting.optimizer import BacktestOptimizer
            
            # Extract price for optimizer
            btc_prices = pd.DataFrame()
            if 'binance' in metrics_map:
                btc_prices = pd.DataFrame(metrics_map['binance']).set_index('timestamp')
            elif 'coingecko' in metrics_map:
                btc_prices = pd.DataFrame(metrics_map['coingecko']).set_index('timestamp')
            
            with st.spinner("Optimizing weights via Optuna..."):
                optimizer = BacktestOptimizer(history, btc_prices)
                results = optimizer.run_optimization(n_trials=30)
                
                if results:
                    st.success(f"Best Correlation: {results['best_value']:.4f}")
                    st.json(results['best_params'])
                    st.info("💡 Update `config/thresholds.yaml` with these values.")
                    
                    # Render backtest results with Priority Hiding pattern
                    if hasattr(optimizer, 'backtest_results') and optimizer.backtest_results:
                        st.markdown("### 📊 BACKTEST RESULTS")
                        render_backtest_table(optimizer.backtest_results, st.session_state.snapshot.get('label', 'NEUTRAL'))

def render_backtest_table(backtest_results: List[Dict[str, Any]], current_regime: str):
    """Renders backtest results table with Priority Hiding pattern and flash effects."""
    
    # Detect regime state change for flash effect
    flash_class = ""
    if 'previous_regime_verdict' in st.session_state:
        if st.session_state.previous_regime_verdict != current_regime:
            flash_class = "regime-flash"
    st.session_state.previous_regime_verdict = current_regime
    
    # Build responsive HTML table with Priority Hiding
    html = f"""
    <style>
    /* Container query for responsive table */
    .backtest-container {{
        container-type: inline-size;
        width: 100%;
    }}
    
    .backtest-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        background: rgba(31, 40, 51, 0.4);
        border: 1px solid #45a29e;
        border-radius: 3px;
        overflow: hidden;
        font-feature-settings: "tnum" 1;
    }}
    
    .backtest-table thead {{
        background: rgba(5, 217, 232, 0.1);
    }}
    
    .backtest-table th {{
        padding: 12px 16px;
        text-align: left;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.75rem;
        color: #05D9E8;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        border-bottom: 2px solid #05D9E8;
    }}
    
    .backtest-table tbody tr {{
        background: rgba(11, 12, 16, 0.6);
        transition: background 0.15s ease-out;
    }}
    
    .backtest-table tbody tr:hover {{
        background: rgba(31, 40, 51, 0.7);
    }}
    
    .backtest-table td {{
        padding: 10px 16px;
        border-bottom: 1px solid rgba(69, 162, 158, 0.2);
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.9);
    }}
    
    /* Priority Hiding: Hide MVRV and Net Flows on mobile */
    .col-priority-low {{
        display: table-cell;
    }}
    
    @container (max-width: 600px) {{
        .col-priority-low {{
            display: none;
        }}
    }}
    
    /* Regime verdict styling */
    .regime-verdict {{
        font-family: 'Orbitron', 'Inter', sans-serif;
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 0.1em;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
    }}
    
    .regime-verdict.BULL {{
        color: #4AF6C3;
        background: rgba(74, 246, 195, 0.1);
        border: 1px solid #4AF6C3;
        text-shadow: 0 0 8px rgba(74, 246, 195, 0.4);
    }}
    
    .regime-verdict.BEAR {{
        color: #FF433D;
        background: rgba(255, 67, 61, 0.1);
        border: 1px solid #FF433D;
        text-shadow: 0 0 8px rgba(255, 67, 61, 0.4);
    }}
    
    .regime-verdict.NEUTRAL {{
        color: #FFD60A;
        background: rgba(255, 214, 10, 0.1);
        border: 1px solid #FFD60A;
        text-shadow: 0 0 8px rgba(255, 214, 10, 0.4);
    }}
    
    /* Flash effect on regime state change (300ms) */
    @keyframes regime-flash {{
        0% {{
            box-shadow: 0 0 0px rgba(5, 217, 232, 0);
            transform: scale(1);
        }}
        50% {{
            box-shadow: 0 0 20px rgba(5, 217, 232, 0.8);
            transform: scale(1.05);
        }}
        100% {{
            box-shadow: 0 0 0px rgba(5, 217, 232, 0);
            transform: scale(1);
        }}
    }}
    
    .regime-flash {{
        animation: regime-flash 300ms ease-out;
    }}
    
    /* Price column styling */
    .price-value {{
        color: #05D9E8;
        font-weight: 700;
    }}
    
    /* Mobile responsiveness hint */
    .mobile-hint {{
        display: none;
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        color: rgba(255, 255, 255, 0.5);
        text-align: center;
        padding: 8px;
        font-style: italic;
    }}
    
    @container (max-width: 600px) {{
        .mobile-hint {{
            display: block;
        }}
    }}
    </style>
    
    <div class="backtest-container">
        <table class="backtest-table">
            <thead>
                <tr>
                    <th>REGIME</th>
                    <th>PRICE</th>
                    <th class="col-priority-low">MVRV</th>
                    <th class="col-priority-low">NET FLOWS</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for result in backtest_results[:10]:  # Limit to 10 most recent
        regime = result.get('regime', 'NEUTRAL')
        price = result.get('price', 0.0)
        mvrv = result.get('mvrv', 0.0)
        net_flows = result.get('net_flows', 0.0)
        
        # Apply flash effect to current regime
        regime_class = f"regime-verdict {regime}"
        if regime == current_regime:
            regime_class += f" {flash_class}"
        
        # Format values
        price_str = f"${price:,.2f}" if price else "N/A"
        mvrv_str = f"{mvrv:.2f}" if mvrv else "N/A"
        net_flows_str = f"{net_flows:,.0f}" if net_flows else "N/A"
        
        html += f"""
            <tr>
                <td><span class="{regime_class}">{regime}</span></td>
                <td class="price-value">{price_str}</td>
                <td class="col-priority-low">{mvrv_str}</td>
                <td class="col-priority-low">{net_flows_str}</td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
        <div class="mobile-hint">📱 Tap row for full details (MVRV, Net Flows)</div>
    </div>
    """
    
    st.html(html)

def render_ticker_tape(snapshot: Dict[str, Any]):
    """Renders a high-frequency ticker tape with JetBrains Mono and tabular alignment."""
    score = snapshot.get('score', 0.0)
    label = snapshot.get('label', 'UNKNOWN')
    
    st.html(f"""
        <style>
        .ticker-tape-container {{
            width: 100%;
            overflow: hidden;
            background: rgba(18, 18, 18, 0.9);
            border-bottom: 1px solid var(--structural-border);
            padding: 4px 0;
            white-space: nowrap;
        }}
        
        .ticker-tape {{
            display: inline-block;
            padding-left: 100%;
            animation: ticker 30s linear infinite;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.85rem;
            color: #E0E0E0;
            font-variant-numeric: tabular-nums lining-nums;
        }}
        
        @keyframes ticker {{
            0% {{ transform: translate(0, 0); }}
            100% {{ transform: translate(-100%, 0); }}
        }}
        
        .ticker-item {{
            margin-right: 2rem;
            display: inline-block;
        }}
        
        .ticker-label {{
            opacity: 0.6;
            margin-right: 0.5rem;
        }}
        
        .ticker-value {{
            font-weight: 700;
        }}
        </style>
        <div class="ticker-tape-container">
            <div class="ticker-tape">
                <span class="ticker-item"><span class="ticker-label">REGIME:</span><span class="ticker-value">{label}</span></span>
                <span class="ticker-item"><span class="ticker-label">SCORE:</span><span class="ticker-value">{score:.2f}</span></span>
                <span class="ticker-item"><span class="ticker-label">BTC/USD:</span><span class="ticker-value">LATEST_TICK</span></span>
                <span class="ticker-item"><span class="ticker-label">DOMINANCE:</span><span class="ticker-value">52.4%</span></span>
            </div>
        </div>
    """)

def render_order_book(mock_data: bool = True):
    """Renders a structural order book component with functional alignment."""
    st.markdown("### 📑 ORDER BOOK DEPTH")
    
    html = """
    <style>
    .order-book-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2px;
        background: #1E1E1E;
        border: 1px solid var(--structural-border);
        padding: 4px;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem;
        font-variant-numeric: tabular-nums lining-nums;
    }
    
    .ob-header {
        opacity: 0.6;
        padding-bottom: 4px;
        border-bottom: 1px solid var(--structural-border);
        margin-bottom: 4px;
        text-transform: uppercase;
        font-size: 0.7rem;
    }
    
    .ob-row {
        display: grid;
        grid-template-columns: 1fr 1.5fr;
        margin-bottom: 2px;
    }
    
    .ob-price {
        font-weight: 700;
        text-align: left;
    }
    
    .ob-size {
        text-align: right;
        opacity: 0.8;
    }
    
    .bid-price { color: var(--finance-green); }
    .ask-price { color: var(--bloomberg-red); }
    </style>
    <div class="order-book-container">
        <div class="ob-column">
            <div class="ob-header">BIDS</div>
            <div class="ob-row"><span class="ob-price bid-price">98442.10</span><span class="ob-size">1.442</span></div>
            <div class="ob-row"><span class="ob-price bid-price">98441.50</span><span class="ob-size">0.088</span></div>
            <div class="ob-row"><span class="ob-price bid-price">98440.00</span><span class="ob-size">2.110</span></div>
        </div>
        <div class="ob-column">
            <div class="ob-header">ASKS</div>
            <div class="ob-row"><span class="ob-price ask-price">98443.50</span><span class="ob-size">0.512</span></div>
            <div class="ob-row"><span class="ob-price ask-price">98444.00</span><span class="ob-size">1.998</span></div>
            <div class="ob-row"><span class="ob-price ask-price">98445.20</span><span class="ob-size">0.021</span></div>
        </div>
    </div>
    """
    st.html(html)

def render_technical_logs(metrics_map: Dict[str, Any], snapshot: Dict[str, Any], mtf: Dict[str, Any]):
    """Renders technical logs and reasoning narrative."""
    with st.expander("🛠️ TECHNICAL LOGS & LOGIC EXPLAINABILITY"):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### RAW DATA STATUS")
            for name, data in metrics_map.items():
                status = "✅ SUCCESS" if data else "❌ FAILED"
                st.write(f"- **{name.upper()}**: {status}")
        
        with col2:
            st.markdown("### 🧠 INTELLIGENCE BRIEFING")
            reasoning = snapshot.get('reasoning', ["Market logic is currently being calculated..."])
            
            # Display bullet points for each reason
            for item in reasoning:
                st.markdown(f"• {item}")
            
            st.caption(f"Engine Version: {snapshot.get('engine_version', '1.0.0')} | Confluence: {mtf.get('confluence_score', 0)}%")
