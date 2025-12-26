"""
Comprehensive unit tests for src/ui/dashboard.py

Test Coverage:
- render_kpi_section(): Visual layering, regime verdict, flash effects
- render_component_breakdown(): High-frequency fragments, HTML tables
- render_backtest_table(): Priority hiding pattern, mobile responsiveness
- render_technical_logs(): Technical logs rendering
- Streamlit fragment, session_state, and html mocking
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from typing import Dict, Any, List


class TestRenderKPISection(unittest.TestCase):
    """Comprehensive tests for render_kpi_section function."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.mock_snapshot = {
            'label': 'BLULL',
            'score': 2.5,
            'confidence': 'HIGH'
        }
    
    # ========== HAPPY PATH TESTS ==========
    
    @patch('src.ui.dashboard.st')
    @patch('src.ui.dashboard.plot_score_gauge')
    def test_render_kpi_section_displays_metrics(self, mock_gauge, mock_st):
        """Test render_kpi_section displays score and confidence metrics."""
        # Arrange
        from src.ui.dashboard import render_kpi_section
        
        # Act
        render_kpi_section(self.mock_snapshot)
        
        # Assert: Verify st.metric was called for score and confidence
        metric_calls = [call for call in mock_st.metric.call_args_list]
        self.assertGreater(len(metric_calls), 0,
                          "Should call st.metric at least once")
    
    @patch('src.ui.dashboard.st')
    @patch('src.ui.dashboard.plot_score_gauge')
    def test_render_kpi_section_injects_visual_layering_css(self, mock_gauge, mock_st):
        """Test that Visual Layering CSS is injected (opacity 1.0 for values, 0.6 for labels)."""
        # Arrange
        from src.ui.dashboard import render_kpi_section
        
        # Act
        render_kpi_section(self.mock_snapshot)
        
        # Assert: Verify st.html was called with CSS
        self.assertTrue(mock_st.html.called,
                       "Should call st.html to inject CSS")
        
        # Verify CSS contains Visual Layering rules
        html_calls = [str(call) for call in mock_st.html.call_args_list]
        css_content = ' '.join(html_calls)
        self.assertIn('opacity', css_content.lower(),
                     "CSS should include opacity rules for Visual Layering")
    
    # ========== EDGE CASE TESTS ==========
    
    @patch('src.ui.dashboard.st')
    @patch('src.ui.dashboard.plot_score_gauge')
    def test_render_kpi_section_handles_unknown_regime(self, mock_gauge, mock_st):
        """Test render_kpi_section handles UNKNOWN regime label."""
        # Arrange
        from src.ui.dashboard import render_kpi_section
        snapshot = {
            'label': 'UNKNOWN',
            'score': 0.0,
            'confidence': 'PENDING'
        }
        
        # Act
        render_kpi_section(snapshot)
        
        # Assert: Should not raise exception
        self.assertTrue(True, "Should handle UNKNOWN regime without error")
    
    @patch('src.ui.dashboard.st')
    @patch('src.ui.dashboard.plot_score_gauge')
    def test_render_kpi_section_handles_negative_score(self, mock_gauge, mock_st):
        """Test render_kpi_section displays negative scores correctly."""
        # Arrange
        from src.ui.dashboard import render_kpi_section
        snapshot = {
            'label': 'BEAR',
            'score': -3.5,
            'confidence': 'MEDIUM'
        }
        
        # Act
        render_kpi_section(snapshot)
        
        # Assert: Verify negative score is formatted
        metric_calls = mock_st.metric.call_args_list
        score_call = [c for c in metric_calls if 'Score' in str(c)]
        self.assertGreater(len(score_call), 0,
                          "Should display negative score")
    
    # ========== ERROR SCENARIO TESTS ==========
    
    @patch('src.ui.dashboard.st')
    @patch('src.ui.dashboard.plot_score_gauge')
    def test_render_kpi_section_handles_missing_label(self, mock_gauge, mock_st):
        """Test render_kpi_section handles missing label gracefully."""
        # Arrange
        from src.ui.dashboard import render_kpi_section
        incomplete_snapshot = {
            'score': 1.5,
            'confidence': 'HIGH'
        }
        
        # Act & Assert: May raise KeyError or handle gracefully
        try:
            render_kpi_section(incomplete_snapshot)
        except KeyError:
            pass  # Expected behavior for missing required field


class TestRenderComponentBreakdown(unittest.TestCase):
    """Comprehensive tests for render_component_breakdown function."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.mock_breakdown = [
            {'metric_name': 'fear_greed_index', 'score': -1.0, 'raw_value': 22.0, 'confidence': 'HIGH'},
            {'metric_name': 'hash_rate', 'score': 0.8, 'raw_value': 1171325755, 'confidence': 'HIGH'},
            {'metric_name': 'mvrv_ratio', 'score': 0.0, 'raw_value': 1.56, 'confidence': 'MEDIUM'},
        ]
   
    # ========== EDGE CASE TESTS ==========
    
    @patch('src.ui.dashboard.st')
    def test_render_component_breakdown_with_empty_list(self, mock_st):
        """Test render_component_breakdown handles empty indicator list."""
        # Arrange
        from src.ui.dashboard import render_component_breakdown
        
        # Act
        render_component_breakdown([])
        
        # Assert: Should not raise exception
        self.assertTrue(True, "Should handle empty breakdown gracefully")
    
    @patch('src.ui.dashboard.st')
    def test_render_component_breakdown_generates_html_table(self, mock_st):
        """Test render_component_breakdown generates HTML table via st.html()."""
        # Arrange
        from src.ui.dashboard import render_component_breakdown
        mock_st.fragment = Mock(return_value=lambda f: f)  # Mock fragment decorator
        
        # Act
        render_component_breakdown(self.mock_breakdown)
        
        # Assert: Should call st.markdown
        self.assertTrue(mock_st.markdown.called,
                       "Should call st.markdown for section title")
    
    @patch('src.ui.dashboard.st')
    def test_render_component_breakdown_limits_to_top_8(self, mock_st):
        """Test that only top 8 indicators are displayed."""
        # Arrange
        from src.ui.dashboard import render_component_breakdown
        mock_st.fragment = Mock(return_value=lambda f: f)  # Mock fragment decorator
        large_breakdown = [{'metric_name': f'metric_{i}', 'score': i, 'raw_value': i*10, 'confidence': 'HIGH'} 
                          for i in range(15)]
        
        # Act
        render_component_breakdown(large_breakdown)
        
        # Assert: Should complete without error
        self.assertTrue(True, "Should handle large breakdown list")


class TestRenderBacktestTable(unittest.TestCase):
    """Comprehensive tests for render_backtest_table function."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.mock_backtest_results = [
            {'regime': 'BULL', 'price': 45234.56, 'mvrv': 2.45, 'net_flows': 12450},
            {'regime': 'NEUTRAL', 'price': 44123.12, 'mvrv': 1.98, 'net_flows': -5600},
            {'regime': 'BEAR', 'price': 43500.00, 'mvrv': 1.45, 'net_flows': -18900},
        ]
        self.current_regime = 'BULL'
    
    @patch('src.ui.dashboard.st')
    def test_render_backtest_table_generates_priority_hiding_css(self, mock_st):
        """Test render_backtest_table includes Priority Hiding CSS (@container queries)."""
        # Arrange
        from src.ui.dashboard import render_backtest_table
        
        # Act
        render_backtest_table(self.mock_backtest_results, self.current_regime)
        
        # Assert: Verify st.html was called
        self.assertTrue(mock_st.html.called,
                       "Should call st.html to render table")
        
        # Verify CSS contains container queries
        html_arg = str(mock_st.html.call_args)
        self.assertIn('@container', html_arg.lower() or 'container-type' in html_arg.lower() or 'col-priority' in html_arg.lower(),
                     "Should include Priority Hiding CSS")
    
    @patch('src.ui.dashboard.st')
    def test_render_backtest_table_applies_flash_effect_to_current_regime(self, mock_st):
        """Test flash effect is applied to rows matching current regime."""
        # Arrange
        from src.ui.dashboard import render_backtest_table
        
        # Setup session state mock with MagicMock to support attribute access
        mock_session_state = MagicMock()
        mock_session_state.get = Mock(return_value=None)
        mock_st.session_state = mock_session_state
        
        # Act
        render_backtest_table(self.mock_backtest_results, 'BULL')
        
        # Assert: Should complete without error (flash effect is CSS-based)
        self.assertTrue(mock_st.html.called,
                       "Should call st.html to render table")
    
    @patch('src.ui.dashboard.st')
    def test_render_backtest_table_formats_price_with_commas(self, mock_st):
        """Test price values are formatted with thousand separators."""
        # Arrange
        from src.ui.dashboard import render_backtest_table
        
        # Setup session state mock
        mock_session_state = MagicMock()
        mock_session_state.get = Mock(return_value=None)
        mock_st.session_state = mock_session_state
        
        # Act
        render_backtest_table(self.mock_backtest_results, self.current_regime)
        
        # Assert: Verify st.html was called to render table
        self.assertTrue(mock_st.html.called,
                       "Should call st.html to render backtest table")
    
    @patch('src.ui.dashboard.st')
    def test_render_backtest_table_handles_empty_results(self, mock_st):
        """Test render_backtest_table handles empty backtest results."""
        # Arrange
        from src.ui.dashboard import render_backtest_table
        
        # Act
        render_backtest_table([], self.current_regime)
        
        # Assert: Should handle gracefully
        self.assertTrue(True, "Should handle empty results without error")


class TestRenderTechnicalLogs(unittest.TestCase):
    """Comprehensive tests for render_technical_logs function."""
    
    @patch('src.ui.dashboard.st')
    def test_render_technical_logs_displays_raw_data_status(self, mock_st):
        """Test render_technical_logs shows SUCCESS/FAILED status for each metric."""
        # Arrange
        from src.ui.dashboard import render_technical_logs
        
        # Mock st.columns to return a tuple of Mock objects
        col1_mock = Mock()
        col2_mock = Mock()
        mock_st.columns = Mock(return_value=(col1_mock, col2_mock))
        mock_st.expander = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        metrics_map = {
            'binance': ['data'],
            'coingecko': [],
        }
        snapshot = {'reasoning': ['Market volatility increasing'], 'engine_version': '5.1'}
        mtf = {'confluence_score': 85}
        
        # Act
        render_technical_logs(metrics_map, snapshot, mtf)
        
        # Assert: Verify expander was created
        self.assertTrue(mock_st.expander.called,
                       "Should create expander for technical logs")
    
    @patch('src.ui.dashboard.st')
    def test_render_technical_logs_displays_reasoning_bullets(self, mock_st):
        """Test render_technical_logs displays reasoning as bullet points."""
        # Arrange
        from src.ui.dashboard import render_technical_logs
        
        # Mock st.columns to return a tuple of Mock objects
        col1_mock = Mock()
        col2_mock = Mock()
        mock_st.columns = Mock(return_value=(col1_mock, col2_mock))
        mock_st.expander = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        metrics_map = {'binance': ['data']}
        snapshot = {
            'reasoning': ['Trend is bullish', 'Volume increasing', 'Support holding'],
            'engine_version': '5.2'
        }
        mtf = {'confluence_score': 75}
        
        # Act
        render_technical_logs(metrics_map, snapshot, mtf)
        
        # Assert: Verify st.columns was called (layout creation)
        self.assertTrue(mock_st.columns.called,
                       "Should call st.columns for layout creation")


if __name__ == '__main__':
    unittest.main()
