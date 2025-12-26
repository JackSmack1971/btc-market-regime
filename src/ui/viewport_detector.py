"""
Viewport Detector for Responsive Priority Hiding

Implements JavaScript bridge to detect viewport width and enable
priority-based column hiding for mobile/tablet optimization.
"""

import streamlit as st


def inject_viewport_detector():
    """Injects viewport detection JavaScript that updates session state."""
    
    st.html("""
        <script>
        (function() {
            function detectViewport() {
                const width = window.innerWidth;
                
                // Update Streamlit session state via postMessage
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    key: 'viewport_width',
                    value: width
                }, '*');
                
                // Log for debugging
                console.log('Viewport width detected:', width);
            }
            
            // Detect on load
            detectViewport();
            
            // Re-detect on resize (debounced)
            let resizeTimer;
            window.addEventListener('resize', function() {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(detectViewport, 150);
            });
        })();
        </script>
    """)


def get_viewport_width(default=1920):
    """
    Get detected viewport width from session state.
    
    Args:
        default: Default width if detection hasn't run yet
        
    Returns:
        int: Viewport width in pixels
    """
    return st.session_state.get('viewport_width', default)


def get_priority_columns(viewport_width):
    """
    Determine which columns to display based on viewport width.
    
    Priority levels:
    - Priority 1: Always visible (Symbol, Price, 24h%)
    - Priority 2: Hidden on mobile <600px (Volume, MVRV)
    - Priority 3: Hidden on tablet <1440px (Net Flows, Sparkline)
    
    Args:
        viewport_width: Current viewport width in pixels
        
    Returns:
        list: Column names to display
    """
    # Priority 1: Always visible
    columns = ['Symbol', 'Price', '24h %']
    
    # Priority 2: Tablet and up
    if viewport_width >= 600:
        columns.extend(['Volume'])
    
    # Priority 3: Desktop only  
    if viewport_width >= 1440:
        columns.extend(['MVRV', 'Net Flows'])
    
    return columns
